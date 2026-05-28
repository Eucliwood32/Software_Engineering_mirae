import typing
import datetime

class ContributionAggregator:
    """
    FR-4 정규화, 가중치 산출, 모든 데이터 소스의 결측치 동적 스케일링
    FR-4.3: 임의의 데이터 소스(Git, 문서, 메신저) 중 일부가 부재하거나
             분석 실패한 경우 해당 소스의 가중치를 0으로 만들고 나머지를
             상대 비율 유지하며 재조정한다.
    """
    def __init__(self, mapping: typing.Dict[str, str]):
        self.mapping = mapping  # { "alias": "팀원이름" }

    def aggregate(self, git_data: dict, doc_data: dict, msg_data: dict, 
                  weights: dict, stopword_dict=None) -> typing.Dict[str, typing.Any]:
        
        # 1. Alias 매핑 적용하여 통합 집계
        raw_git = {}
        raw_doc = {}
        raw_msg = {}
        
        # Git (값은 Detectors.apply_capping 에서 log1p 적용된 float)
        for alias, val in git_data.items():
            if alias in self.mapping:
                mapped_name = self.mapping[alias]
                raw_git[mapped_name] = raw_git.get(mapped_name, 0.0) + val
                
        # Doc
        for alias, count in doc_data.items():
            if alias in self.mapping:
                mapped_name = self.mapping[alias]
                raw_doc[mapped_name] = raw_doc.get(mapped_name, 0) + count
                
        # Msg
        if msg_data and "records" in msg_data:
            for record in msg_data["records"]:
                alias = record["author"]
                if alias in self.mapping:
                    if stopword_dict:
                        if not stopword_dict.is_meaningful_message(record["message"]):
                            continue
                    mapped_name = self.mapping[alias]
                    raw_msg[mapped_name] = raw_msg.get(mapped_name, 0) + 1
                    
        team_members = set(self.mapping.values())
        
        # 2. 정규화 (Min-Max) — FR-4.1
        def _normalize(raw_dict):
            if not team_members: return {}
            vals = [raw_dict.get(m, 0.0) for m in team_members]
            min_v = min(vals)
            max_v = max(vals)
            norm = {}
            for m in team_members:
                v = raw_dict.get(m, 0.0)
                if max_v == min_v:
                    norm[m] = 0.5
                else:
                    norm[m] = round((v - min_v) / (max_v - min_v), 4)
            return norm
            
        norm_git = _normalize(raw_git)
        norm_doc = _normalize(raw_doc)
        norm_msg = _normalize(raw_msg)
        
        # 3. FR-4.3 모든 데이터 소스의 결측 동적 가중치 재조정
        w_git = weights.get("git", 0.4)
        w_doc = weights.get("doc", 0.4)
        w_msg = weights.get("msg", 0.2)
        
        git_missing = not git_data or len(git_data) == 0
        doc_missing = not doc_data or len(doc_data) == 0
        msg_missing = not msg_data or "error" in msg_data or "records" not in msg_data
        
        missing_sources = []
        if git_missing: missing_sources.append("Git")
        if doc_missing: missing_sources.append("문서")
        if msg_missing: missing_sources.append("메신저")
        
        # 가중치 재조정
        source_weights = {"git": w_git, "doc": w_doc, "msg": w_msg}
        if git_missing: source_weights["git"] = 0.0
        if doc_missing: source_weights["doc"] = 0.0
        if msg_missing: source_weights["msg"] = 0.0
        
        available_sum = sum(source_weights.values())
        
        if available_sum > 0:
            # 상대 비율 유지 스케일링
            for k in source_weights:
                source_weights[k] = source_weights[k] / available_sum
        else:
            # 3개 소스 모두 부재 — FR-4.3: 이 경우는 controller에서 사전 차단
            pass
            
        w_git = source_weights["git"]
        w_doc = source_weights["doc"]
        w_msg = source_weights["msg"]
        
        # 검증
        weight_sum = round(w_git + w_doc + w_msg, 4)
        assert weight_sum == 1.0 or available_sum == 0, \
            f"Weight sum error: {w_git}+{w_doc}+{w_msg}={weight_sum}"
        
        # 4. 종합 지표 산출
        result_scores = {}
        for m in team_members:
            score = ((norm_git.get(m, 0.0) * w_git) + 
                     (norm_doc.get(m, 0.0) * w_doc) + 
                     (norm_msg.get(m, 0.0) * w_msg))
            result_scores[m] = {
                "git": norm_git.get(m, 0.0),
                "doc": norm_doc.get(m, 0.0),
                "msg": norm_msg.get(m, 0.0),
                "total": round(score, 4),
                "raw_msg_count": raw_msg.get(m, 0),
                "raw_doc_count": raw_doc.get(m, 0),
                "raw_git_additions": raw_git.get(m, 0.0)
            }
            
        return {
            "scores": result_scores,
            "weights_used": {"git": w_git, "doc": w_doc, "msg": w_msg},
            "missing_sources": missing_sources,
            "analysis_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
