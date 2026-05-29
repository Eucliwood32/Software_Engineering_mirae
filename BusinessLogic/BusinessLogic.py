"""
BusinessLogic.py

QCE(Quantitative Contribution Evaluator) 시스템의 Model · BusinessLogic 레이어
참조 문서: 
- Architecture Overview v1.1
- Model Business Logic Design v1.1
- Development Constraints v2.0 (C-4, C-8)
"""

import math
import json
import os
import csv
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

# ==========================================
# 1. 공용 데이터 타입 (Architecture Overview §5.1)
# ==========================================

@dataclass
class CommitStats:
    commits: int
    additions: int
    deletions: int

@dataclass
class MessengerRecord:
    author: str
    timestamp: str
    message: str

@dataclass
class ParseResult:
    records: List[MessengerRecord]
    skipped_lines: int

@dataclass
class MemberScore:
    author: str
    git_score: float
    doc_score: float
    msg_score: float
    total_score: float
    raw_additions: int
    raw_char_count: int
    raw_msg_count: int
    capping_applied: bool
    anomaly_flags: List[str] = field(default_factory=list)


# ==========================================
# 2. 컴포넌트 구현 (Model Business Logic Design)
# ==========================================

class Normalizer:
    """FR-4.1: 이질적 단위 지표를 0.0~1.0 척도로 변환 (Min-Max 정규화)"""
    def normalize(self, values: List[float]) -> List[float]:
        if not values:
            return []
        
        val_min = min(values)
        val_max = max(values)
        
        # ZeroDivisionError 방지 및 분산이 없는 경우 전원 0.5 처리
        if val_min == val_max:
            return [0.5] * len(values)
            
        return [round((v - val_min) / (val_max - val_min), 4) for v in values]


class CappingScaler:
    """FR-4.2: 비정상적 대량 추가에 의한 지표 왜곡 방지 (상한 제한 및 로그 스케일링)"""
    CAPPING_THRESHOLD: int = 1000

    def cap(self, additions: int) -> Tuple[int, bool]:
        if additions > self.CAPPING_THRESHOLD:
            return (1000, True)
        return (additions, False)

    def log_scale(self, total: int) -> float:
        if total == 0:
            return 0.0
        return round(math.log1p(total), 4)


class AnomalySignalDetector:
    """
    FR-4.2b, FR-4.2c: 통계적/규칙적 이상 징후 식별 신호 생성.
    (ConOps P5 원칙에 따라 점수에 자동 반영되지 않으며, 표시 전용 데이터입니다.)
    """
    def detect_frequency(self, repo: Dict[str, CommitStats]) -> List[dict]:
        """
        EW-02: 특정 일자 커밋 수가 일평균 커밋 수 3배 초과 시 신호 발생.
        (본 메서드는 입력 시그니처 상의 데이터만으로 구현 불가능한 확장 스펙이므로 
        시계열 데이터가 추후 제공된다고 가정하고 기본 리스트를 반환합니다.)
        """
        return []

    def detect_zscore(self, scores: List[MemberScore]) -> List[str]:
        """FR-4.2c: 정규화 지표 중 Z-Score ≤ -1.5 인 지표가 2개 이상인 팀원 반환"""
        if not scores:
            return []
        
        git_vals = [s.git_score for s in scores]
        doc_vals = [s.doc_score for s in scores]
        msg_vals = [s.msg_score for s in scores]
        
        def calculate_zscores(vals: List[float]) -> List[float]:
            n = len(vals)
            if n == 0: return []
            mean = sum(vals) / n
            variance = sum((x - mean)**2 for x in vals) / n
            std = math.sqrt(variance)
            if std == 0: return [0.0] * n
            return [(x - mean) / std for x in vals]
            
        git_z = calculate_zscores(git_vals)
        doc_z = calculate_zscores(doc_vals)
        msg_z = calculate_zscores(msg_vals)
        
        flagged_authors = []
        for i, score in enumerate(scores):
            anomalies = 0
            if git_z and git_z[i] <= -1.5: anomalies += 1
            if doc_z and doc_z[i] <= -1.5: anomalies += 1
            if msg_z and msg_z[i] <= -1.5: anomalies += 1
            
            if anomalies >= 2:
                flagged_authors.append(score.author)
                
        return flagged_authors


class WeightPresetManager:
    """FR-4.4: 3가지 가중치 프리셋 관리 및 커스텀 합계 검증"""
    PRESETS: Dict[str, Tuple[float, float, float]] = {
        "개발 중심": (0.60, 0.25, 0.15),
        "기획 중심": (0.20, 0.60, 0.20),
        "균형 설정": (0.40, 0.40, 0.20)
    }

    def validate_sum(self, w_git: float, w_doc: float, w_msg: float) -> bool:
        """부동소수점 오차 ±0.0001 허용하여 합계가 1.0인지 검증"""
        return abs(w_git + w_doc + w_msg - 1.0) < 0.0001


class WeightRebalancer:
    """FR-4.3: 일부 소스가 결측된 경우 나머지 소스의 상대 비율을 유지하여 1.0으로 재정규화"""
    def rebalance(self, weights: Dict[str, float], available: Set[str]) -> Dict[str, float]:
        if not available:
            raise ValueError("분석 가능한 데이터 소스가 없습니다.")
            
        available_sum = sum(weights[k] for k in available if k in weights)
        
        rebalanced = {}
        for k, v in weights.items():
            if k in available:
                if available_sum > 0:
                    rebalanced[k] = v / available_sum
                else:
                    # 기존 비율이 모두 0이었던 경우 1/N 배분
                    rebalanced[k] = 1.0 / len(available)
            else:
                rebalanced[k] = 0.0
                
        return rebalanced


class AliasMapper:
    """FR-1.3: 파싱된 원시 식별자를 조장이 지정한 단일 팀원(Person)으로 N:1 병합"""
    def merge(self, raw: Dict[str, dict], mapping: Dict[str, str]) -> Dict[str, dict]:
        merged = {}
        for alias, metrics in raw.items():
            if alias not in mapping:
                continue  # 미매핑 alias는 결과에서 제외
                
            person = mapping[alias]
            if person not in merged:
                merged[person] = {}
                
            for m_key, m_val in metrics.items():
                if m_key not in merged[person]:
                    merged[person][m_key] = 0
                merged[person][m_key] += m_val
                
        return merged


class ContributionAggregator:
    """FR-4.*: 지표 통합 파이프라인 (Orchestrator로부터 입력받아 통합 점수 산출)"""
    def __init__(self):
        self.normalizer = Normalizer()
        self.capping_scaler = CappingScaler()
        self.anomaly_detector = AnomalySignalDetector()
        
    def aggregate(self, 
                  git_data: Dict[str, int],  # {author: additions}
                  doc_data: Dict[str, int],  # {author: chars}
                  msg_data: Dict[str, int],  # {author: messages}
                  weights: Dict[str, float]) -> List[MemberScore]:
        
        # 통합 인원 집합
        authors = sorted(list(set(git_data.keys()) | set(doc_data.keys()) | set(msg_data.keys())))
        
        raw_additions = [git_data.get(a, 0) for a in authors]
        raw_docs = [doc_data.get(a, 0) for a in authors]
        raw_msgs = [msg_data.get(a, 0) for a in authors]
        
        # Git Capping & Log Scaling 적용
        log_additions = []
        capping_flags = []
        for add in raw_additions:
            capped_val, is_capped = self.capping_scaler.cap(add)
            capping_flags.append(is_capped)
            log_additions.append(self.capping_scaler.log_scale(capped_val))
            
        # Min-Max 정규화 적용
        git_norm = self.normalizer.normalize(log_additions)
        doc_norm = self.normalizer.normalize(raw_docs)
        msg_norm = self.normalizer.normalize(raw_msgs)
        
        scores = []
        for i, author in enumerate(authors):
            g = git_norm[i]
            d = doc_norm[i]
            m = msg_norm[i]
            
            # 최종 점수 산출 (가중치 적용)
            total = (g * weights.get('git', 0.0)) + (d * weights.get('doc', 0.0)) + (m * weights.get('msg', 0.0))
            
            score_obj = MemberScore(
                author=author,
                git_score=g,
                doc_score=d,
                msg_score=m,
                total_score=total,
                raw_additions=raw_additions[i],
                raw_char_count=raw_docs[i],
                raw_msg_count=raw_msgs[i],
                capping_applied=capping_flags[i],
                anomaly_flags=[]
            )
            scores.append(score_obj)
            
        # 신호탐지 실행 및 플래그 갱신
        z_score_anomalies = self.anomaly_detector.detect_zscore(scores)
        for s in scores:
            if s.author in z_score_anomalies:
                s.anomaly_flags.append("ZSCORE")
            if s.capping_applied:
                s.anomaly_flags.append("CAPPING")
                
        return scores


class CacheManager:
    """NFR-2.3, NFR-2.4, C-8: 원자적 JSON 캐싱 시스템 (pickle 사용 철저히 배제)"""
    def save(self, data: dict, path: str) -> None:
        temp_path = path + ".tmp"
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, path) # 원자적 덮어쓰기
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
            
    def load(self, path: str) -> dict:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}


class ReportExporter:
    """FR-5.2, FR-5.3: 평가 결과 보고서(CSV 등) 추출 (STR-7 판정 금지 용어 준수)"""
    def export_csv(self, scores: List[MemberScore], path: str) -> None:
        # 엑셀 호환을 위해 UTF-8 BOM 인코딩을 사용
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                '팀원(Author)', '종합 지표(Total)', 'Git 지표', '문서 지표', '메신저 지표', 
                'Git 변경량(원시)', '문서 글자수(원시)', '메시지 발화(원시)', 
                'Capping 제한 적용', '확인 필요(Anomaly)'
            ])
            
            # 종합 지표 기준 내림차순 정렬하여 익스포트
            sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)
            
            for s in sorted_scores:
                writer.writerow([
                    s.author, 
                    round(s.total_score, 4), 
                    round(s.git_score, 4), 
                    round(s.doc_score, 4), 
                    round(s.msg_score, 4), 
                    s.raw_additions, 
                    s.raw_char_count, 
                    s.raw_msg_count, 
                    'O' if s.capping_applied else 'X',
                    ", ".join(s.anomaly_flags) if s.anomaly_flags else ""
                ])