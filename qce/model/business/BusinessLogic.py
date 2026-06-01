"""
BusinessLogic.py

QCE(Quantitative Contribution Evaluator) 시스템의 Model · BusinessLogic 레이어
참조 문서: 
- Architecture Overview v1.3
- Model Business Logic Design v1.4
- Development Constraints v2.0 (C-4, C-8)
"""

import math
import re
import dataclasses
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union

from qce.model.business.cache_manager import CacheManager  # noqa: F401 (re-export)
from qce.model.business.report_exporter import ReportExporter  # noqa: F401 (re-export)

# ==========================================
# 1. 공용 데이터 타입 (Architecture Overview §5.1)
# ==========================================

@dataclass
class CommitStats:
    commits: int
    additions: int
    deletions: int
    commits_list: list = field(default_factory=list)

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
    raw_chars: int
    raw_messages: int
    capping_applied: bool
    signals: List[str] = field(default_factory=list)
    signal_details: List[dict] = field(default_factory=list)
    commit_dates: List[str] = field(default_factory=list)
    dimensions: Dict[str, float] = field(default_factory=dict)  # v1.7 레이더 세부 축(표시 전용)


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
        return math.log1p(total)


class AnomalySignalDetector:
    """
    FR-4.2, FR-4.2b, FR-4.2d: 통계적/규칙적 이상 징후 식별 신호 생성.
    (ConOps P5 원칙에 따라 점수에 자동 반영되지 않으며, 표시 전용 데이터입니다.)
    """
    def detect_frequency(self, repo: Dict[str, CommitStats]) -> List[dict]:
        """EW-02: 작성자 단기 커밋 빈도가 평소 일평균의 3배 초과 구간을 신호로."""
        signals = []
        for author, stats in repo.items():
            if not stats.commits_list:
                continue
            
            daily_counts = {}
            for c in stats.commits_list:
                date = c.get("date", "")
                if date:
                    daily_counts[date] = daily_counts.get(date, 0) + 1
                    
            if not daily_counts:
                continue
                
            num_days = len(daily_counts)
            total_commits = sum(daily_counts.values())
            baseline_avg = total_commits / num_days
            
            for date, day_commits in daily_counts.items():
                if baseline_avg > 0 and day_commits > baseline_avg * 3:
                    signals.append({
                        "author": author,
                        "period": date,
                        "period_commits": day_commits,
                        "baseline_avg": round(baseline_avg, 4)
                    })
        return signals

    def detect_capping(self, repo: Dict[str, CommitStats]) -> List[dict]:
        """FR-4.2: 단일 커밋 추가 라인 > 1000인 커밋을 신호로."""
        signals = []
        for author, stats in repo.items():
            for c in stats.commits_list:
                additions = c.get("additions", 0)
                if additions > CappingScaler.CAPPING_THRESHOLD:
                    signals.append({
                        "author": author,
                        "hash": c.get("hash", "")[:7],
                        "date": c.get("date", ""),
                        "additions": additions
                    })
        return signals

    def detect_zscore_detail(self, scores: List[MemberScore]) -> List[dict]:
        """FR-4.2d: 정규화 지표 중 Z-Score <= -1.5 인 지표가 2개 이상인 팀원 상세 반환"""
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
        
        details = []
        for i, score in enumerate(scores):
            metrics = []
            if git_z and git_z[i] <= -1.5: metrics.append("git")
            if doc_z and doc_z[i] <= -1.5: metrics.append("doc")
            if msg_z and msg_z[i] <= -1.5: metrics.append("msg")
            
            if len(metrics) >= 2:
                details.append({
                    "author": score.author,
                    "metrics": metrics
                })
        return details

    def detect_zscore(self, scores: List[MemberScore]) -> List[str]:
        return [d["author"] for d in self.detect_zscore_detail(scores)]

    def build_signal_details(
        self, repo: Optional[Dict[str, CommitStats]], scores: List[MemberScore]
    ) -> Dict[str, List[dict]]:
        result = {s.author: [] for s in scores}
        
        if repo:
            capping_signals = self.detect_capping(repo)
            for sig in capping_signals:
                author = sig.pop("author")
                if author in result:
                    sig["type"] = "CAPPING"
                    result[author].append(sig)
                    
            freq_signals = self.detect_frequency(repo)
            for sig in freq_signals:
                author = sig.pop("author")
                if author in result:
                    sig["type"] = "EW-02"
                    result[author].append(sig)
                    
        zscore_signals = self.detect_zscore_detail(scores)
        for sig in zscore_signals:
            author = sig.pop("author")
            if author in result:
                sig["type"] = "ZSCORE"
                result[author].append(sig)
                
        return result


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

    def preset_names(self) -> List[str]:
        return list(self.PRESETS.keys())

    def get_preset(self, name: str) -> Dict[str, float]:
        if name in self.PRESETS:
            g, d, m = self.PRESETS[name]
            return {"git": g, "doc": d, "msg": m}
        return {"git": 0.4, "doc": 0.4, "msg": 0.2}

    def match_preset(self, w_git: float, w_doc: float, w_msg: float) -> Optional[str]:
        for name, (g, d, m) in self.PRESETS.items():
            if abs(w_git - g) < 1e-4 and abs(w_doc - d) < 1e-4 and abs(w_msg - m) < 1e-4:
                return name
        return None

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def normalize(self, weights: Dict[str, float]) -> Dict[str, float]:
        keys = ["git", "doc", "msg"]
        vals = [max(0.0, weights.get(k, 0.0)) for k in keys]
        total = sum(vals)
        if total == 0:
            vals = [1/3, 1/3, 1/3]
        else:
            vals = [v / total for v in vals]
            
        result = {}
        for i, k in enumerate(keys):
            result[k] = round(vals[i], 4)
            
        current_sum = sum(result.values())
        diff = 1.0 - current_sum
        if abs(diff) > 0:
            result["msg"] = round(result["msg"] + diff, 4)
            
        return result

    def redistribute(self, changed_key: str, new_value: float, current: Dict[str, float]) -> Dict[str, float]:
        if changed_key not in {"git", "doc", "msg"}:
            raise ValueError(f"Unknown weight key: {changed_key!r}")
        fixed_val = self.clamp(new_value)
        result = {changed_key: fixed_val}
        
        remaining = 1.0 - fixed_val
        other_keys = [k for k in ["git", "doc", "msg"] if k != changed_key]
        
        other_sum = sum(max(0.0, current.get(k, 0.0)) for k in other_keys)
        
        if other_sum == 0:
            for k in other_keys:
                result[k] = remaining / len(other_keys)
        else:
            for k in other_keys:
                ratio = max(0.0, current.get(k, 0.0)) / other_sum
                result[k] = remaining * ratio
                
        for k in result:
            result[k] = round(result[k], 4)
            
        current_sum = sum(result.values())
        diff = 1.0 - current_sum
        if abs(diff) > 0:
            last_key = other_keys[-1]
            result[last_key] = round(result[last_key] + diff, 4)
            
        return result


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
                    rebalanced[k] = 1.0 / len(available)
            else:
                rebalanced[k] = 0.0
                
        return rebalanced


class AliasMapper:
    """FR-1.3: 파싱된 원시 식별자를 조장이 지정한 단일 팀원(Person)으로 N:1 병합"""
    def merge(self, raw: dict, mapping: dict) -> dict:
        merged = {}
        for alias, metrics in raw.items():
            if alias not in mapping:
                continue
            target = mapping[alias]
            if target not in merged:
                if hasattr(metrics, "commits"):
                    merged[target] = type(metrics)(0, 0, 0, [])
                elif isinstance(metrics, (int, float)):
                    merged[target] = 0
                else:
                    merged[target] = {}
            
            if hasattr(metrics, "commits"):
                merged[target].commits += metrics.commits
                merged[target].additions += metrics.additions
                merged[target].deletions += metrics.deletions
                merged[target].commits_list.extend(metrics.commits_list)
            elif isinstance(metrics, (int, float)):
                merged[target] += metrics
            else:
                for k, v in metrics.items():
                    merged[target][k] = merged[target].get(k, 0) + v
        return merged


class ContributionAggregator:
    """FR-4.*: 지표 통합 파이프라인 (Orchestrator로부터 입력받아 통합 점수 산출)"""
    def __init__(self):
        self.normalizer = Normalizer()
        self.capping_scaler = CappingScaler()
        self.anomaly_detector = AnomalySignalDetector()
        self.weight_rebalancer = WeightRebalancer()
        
    def aggregate(self,
                  git: Optional[Dict[str, CommitStats]] = None,
                  docs: Optional[Dict[str, int]] = None,
                  msgs: Optional[Dict[str, int]] = None,
                  weights: Optional[Dict[str, float]] = None,
                  doc_details: Optional[Dict[str, dict]] = None,
                  msg_details: Optional[Dict[str, dict]] = None) -> List[MemberScore]:
        if weights is None:
            weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        
        # 1. 가용 소스 판별
        available: Set[str] = set()
        if git is not None:
            available.add("git")
        if docs is not None:
            available.add("doc")
        if msgs is not None:
            available.add("msg")

        if not available:
            return []

        # 2. 가중치 재조정 (결측 소스 처리)
        rebalanced = self.weight_rebalancer.rebalance(weights, available)
        
        # 3. 통합 인원 집합
        author_set: Set[str] = set()
        if git is not None:
            author_set |= set(git.keys())
        if docs is not None:
            author_set |= set(docs.keys())
        if msgs is not None:
            author_set |= set(msgs.keys())
        authors = sorted(list(author_set))
        
        # 4. 원시 값 추출 및 커밋 일자 추출
        raw_additions = []
        raw_docs_vals = []
        raw_msgs_vals = []
        commit_dates_list = []
        
        for a in authors:
            if git is not None and a in git:
                raw_additions.append(git[a].additions)
                dates = sorted(list(set(c.get("date", "") for c in git[a].commits_list if c.get("date"))))
                commit_dates_list.append(dates)
            else:
                raw_additions.append(0)
                commit_dates_list.append([])
                
            raw_docs_vals.append(docs.get(a, 0) if docs is not None else 0)
            raw_msgs_vals.append(msgs.get(a, 0) if msgs is not None else 0)
        
        # 5. Git Capping & Log Scaling 적용
        log_additions = []
        capping_flags = []
        for add in raw_additions:
            capped_val, is_capped = self.capping_scaler.cap(add)
            capping_flags.append(is_capped)
            log_additions.append(self.capping_scaler.log_scale(capped_val))
            
        # 6. Min-Max 정규화 적용
        git_norm = self.normalizer.normalize(log_additions) if git is not None else [0.0] * len(authors)
        doc_norm = self.normalizer.normalize(raw_docs_vals) if docs is not None else [0.0] * len(authors)
        msg_norm = self.normalizer.normalize(raw_msgs_vals) if msgs is not None else [0.0] * len(authors)

        # 6b. 레이더 세부 축(dimensions) 산출 — 가용 소스별 3개 세부 지표 정규화 (v1.7, 표시 전용)
        dimensions_list = self._compute_dimensions(
            authors, git, docs, msgs,
            git_norm=git_norm, doc_norm=doc_norm, msg_norm=msg_norm,
            doc_details=doc_details, msg_details=msg_details,
        )

        # 7. MemberScore 조립
        scores = []
        for i, author in enumerate(authors):
            g = git_norm[i]
            d = doc_norm[i]
            m = msg_norm[i]
            
            total = (g * rebalanced.get('git', 0.0)) + \
                    (d * rebalanced.get('doc', 0.0)) + \
                    (m * rebalanced.get('msg', 0.0))
            
            score_obj = MemberScore(
                author=author,
                git_score=g,
                doc_score=d,
                msg_score=m,
                total_score=round(total, 4),
                raw_additions=raw_additions[i],
                raw_chars=raw_docs_vals[i],
                raw_messages=raw_msgs_vals[i],
                capping_applied=capping_flags[i],
                signals=[],
                signal_details=[],
                commit_dates=commit_dates_list[i],
                dimensions=dimensions_list[i],
            )
            scores.append(score_obj)
            
        # 8. 신호탐지 실행 및 플래그 갱신
        details = self.anomaly_detector.build_signal_details(git, scores)
        
        for s in scores:
            if s.author in details:
                s.signal_details = details[s.author]
                s.signals = sorted(list(set(d.get("type") for d in s.signal_details)))

        return scores

    @staticmethod
    def _git_field(stats, name: str) -> float:
        """git 값(CommitStats 또는 dict) 양쪽에서 필드를 읽는다."""
        if hasattr(stats, name):
            return getattr(stats, name) or 0
        if isinstance(stats, dict):
            return stats.get(name, 0) or 0
        return 0

    def _compute_dimensions(self, authors, git, docs, msgs, *,
                            git_norm, doc_norm, msg_norm,
                            doc_details, msg_details) -> List[Dict[str, float]]:
        """레이더 세부 축(dimensions) 산출 (v1.7). 가용 소스마다 3개 세부 지표를 0~1 정규화한다.
        문서·메신저는 세부 데이터(doc_details/msg_details)가 주어진 경우에만 키를 채운다.
        모든 값은 표시 전용으로 total_score에 반영되지 않는다(STR-7)."""
        n = len(authors)
        dims: List[Dict[str, float]] = [dict() for _ in range(n)]

        # Git: 커밋 수 / 코드 추가(이미 capping+log 정규화한 git_norm 재사용) / 코드 정리(삭제 log)
        if git is not None:
            commits_raw = [self._git_field(git.get(a), "commits") if a in git else 0 for a in authors]
            del_log = [self.capping_scaler.log_scale(int(self._git_field(git.get(a), "deletions")))
                       if a in git else 0.0 for a in authors]
            commits_norm = self.normalizer.normalize(commits_raw)
            del_norm = self.normalizer.normalize(del_log)
            for i in range(n):
                dims[i]["git_commits"] = commits_norm[i]
                dims[i]["git_additions"] = git_norm[i]
                dims[i]["git_deletions"] = del_norm[i]

        # 문서: 글자수(doc_norm 재사용) / 문서 수 / 구성 요소 수
        if docs is not None and doc_details:
            count_raw = [doc_details.get(a, {}).get("docs", 0) for a in authors]
            block_raw = [doc_details.get(a, {}).get("blocks", 0) for a in authors]
            count_norm = self.normalizer.normalize(count_raw)
            block_norm = self.normalizer.normalize(block_raw)
            for i in range(n):
                dims[i]["doc_chars"] = doc_norm[i]
                dims[i]["doc_count"] = count_norm[i]
                dims[i]["doc_blocks"] = block_norm[i]

        # 메신저: 발화 수(msg_norm 재사용) / 발화 글자수 / 활동 시간대 수
        if msgs is not None and msg_details:
            chars_raw = [msg_details.get(a, {}).get("chars", 0) for a in authors]
            hours_raw = [msg_details.get(a, {}).get("hours", 0) for a in authors]
            chars_norm = self.normalizer.normalize(chars_raw)
            hours_norm = self.normalizer.normalize(hours_raw)
            for i in range(n):
                dims[i]["msg_count"] = msg_norm[i]
                dims[i]["msg_chars"] = chars_norm[i]
                dims[i]["msg_hours"] = hours_norm[i]

        return dims


class NormalizedSignalsTracker:
    """FR-4.2c: 조장이 정상 처리한 이상 신호를 세션 내 예외 상태로 기억"""
    def __init__(self):
        self._dismissed: Set[Tuple[str, str, str]] = set()
        
    def dismiss(self, author: str, signal_type: str, ref: str = "") -> None:
        self._dismissed.add((author, signal_type, ref))
        
    def restore(self, author: str, signal_type: str, ref: str = "") -> None:
        self._dismissed.discard((author, signal_type, ref))
        
    def is_dismissed(self, author: str, signal_type: str, ref: str = "") -> bool:
        return (author, signal_type, ref) in self._dismissed
        
    def clear(self) -> None:
        self._dismissed.clear()

    def dismissed_count(self) -> int:
        return len(self._dismissed)

    @staticmethod
    def ref_of(detail: dict) -> str:
        t = detail.get("type", "")
        if t == "CAPPING":
            return detail.get("hash", "")
        elif t == "EW-02":
            return detail.get("period") or detail.get("date", "")
        return ""
        
    def filter_details(self, author: str, details: List[dict]) -> List[dict]:
        filtered = []
        for d in details:
            t = d.get("type", "")
            ref = self.ref_of(d)
            if not self.is_dismissed(author, t, ref):
                filtered.append(d)
        return filtered
        
    def apply(self, scores: List[MemberScore]) -> List[MemberScore]:
        result = []
        for s in scores:
            new_details = self.filter_details(s.author, s.signal_details)
            remaining_types = set(d.get("type") for d in new_details)
            
            new_signals = []
            for sig in s.signals:
                if sig in ("CAPPING", "EW-02", "ZSCORE"):
                    if sig in remaining_types:
                        new_signals.append(sig)
                else:
                    new_signals.append(sig)
                    
            new_score = dataclasses.replace(
                s, 
                signal_details=new_details,
                signals=new_signals
            )
            result.append(new_score)
        return result


class AliasExtractor:
    """FR-1.3: 식별자 수집 및 결정론적 군집화로 N:1 병합 후보 제안"""
    @staticmethod
    def normalize_key(alias: str) -> str:
        local_part = str(alias).split("@")[0]
        norm = re.sub(r'[\s\._\-]', '', local_part)
        return norm.lower()
        
    def extract_identifiers(self, git: Optional[Dict[str, CommitStats]], docs: Optional[Dict[str, int]], msgs: Optional[Dict[str, int]]) -> List[dict]:
        identifiers = []
        
        if git:
            for alias, stats in git.items():
                identifiers.append({"raw_id": alias, "source": "git", "activity": stats.additions})
        if docs:
            for alias, chars in docs.items():
                identifiers.append({"raw_id": alias, "source": "doc", "activity": chars})
        if msgs:
            for alias, count in msgs.items():
                identifiers.append({"raw_id": alias, "source": "msg", "activity": count})
                
        identifiers.sort(key=lambda x: (x["raw_id"], x["source"]))
        return identifiers
        
    def unique_aliases(self, identifiers: List[dict]) -> List[str]:
        aliases = set(d["raw_id"] for d in identifiers)
        aliases.discard("Unknown")
        aliases.discard("")
        return sorted(list(aliases))
        
    def suggest_groups(self, aliases: List[str]) -> Dict[str, List[str]]:
        aliases = [a for a in aliases if a not in ("Unknown", "")]
        groups = {}
        for alias in aliases:
            key = self.normalize_key(alias)
            if key not in groups:
                groups[key] = []
            groups[key].append(alias)
            
        def representative_key(a: str) -> tuple:
            has_korean = bool(re.search(r'[가-힣]', a))
            return (not has_korean, -len(a), a)
            
        result = {}
        for key, members in groups.items():
            members.sort(key=representative_key)
            rep = members[0]
            result[rep] = sorted(members)
            
        return result
        
    def suggest_mapping(self, identifiers: List[dict]) -> Dict[str, str]:
        aliases = self.unique_aliases(identifiers)
        groups = self.suggest_groups(aliases)
        mapping = {}
        for rep, members in groups.items():
            for m in members:
                mapping[m] = rep
        return mapping