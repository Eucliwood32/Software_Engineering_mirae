import typing
import math
import statistics

class Detectors:
    """
    FR-4.2 이상치 Capping 적용
    """
    @staticmethod
    def apply_capping(git_data: typing.Dict[str, typing.Dict[str, typing.Any]]) -> typing.Tuple[typing.Dict[str, float], typing.List[typing.Dict[str, str]]]:
        result = {}
        capping_signals = []
        
        for author, data in git_data.items():
            total_capped_adds = 0
            for commit in data.get("commits_list", []):
                adds = commit.get("additions", 0)
                if adds > 1000:
                    capping_signals.append({
                        "author": author,
                        "hash": commit["hash"][:7],
                        "date": commit["date"],
                        "additions": adds
                    })
                    adds = 1000
                total_capped_adds += adds
                
            result[author] = math.log1p(total_capped_adds)
            
        return result, capping_signals

class FrequencyAnomalyDetector:
    """
    FR-4.2b: 빈도 폭주 신호
    """
    @staticmethod
    def detect(git_data: typing.Dict[str, typing.Dict[str, typing.Any]]) -> typing.List[str]:
        signals = set()
        for author, data in git_data.items():
            daily_counts = {}
            for commit in data.get("commits_list", []):
                date_str = commit["date"].split()[0] if commit["date"] else "unknown"
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                
            counts = list(daily_counts.values())
            if not counts:
                continue
            mean = sum(counts) / len(counts)
            
            if mean > 0:
                for c in counts:
                    if c > mean * 3:
                        signals.add(author)
                        break
        return list(signals)

class ZScoreAnomalyDetector:
    """
    FR-4.2d: Z-Score 하위 이상치 신호
    Z-Score <= -1.5 인 지표가 2개 이상인 팀원 반환
    """
    @staticmethod
    def detect(normalized_scores: typing.Dict[str, typing.Dict[str, float]]) -> typing.List[str]:
        signals = []
        
        if not normalized_scores:
            return signals
            
        authors = list(normalized_scores.keys())
        if len(authors) < 2:
            return signals
            
        metrics = ["git", "doc", "msg"]
        z_scores = {a: {} for a in authors}
        
        for m in metrics:
            vals = [normalized_scores[a].get(m, 0.0) for a in authors]
            try:
                mean = statistics.mean(vals)
                stdev = statistics.stdev(vals) if len(vals) > 1 else 0.0
            except Exception:
                mean, stdev = 0.0, 0.0
                
            for a in authors:
                val = normalized_scores[a].get(m, 0.0)
                if stdev > 0:
                    z = (val - mean) / stdev
                else:
                    z = 0.0
                z_scores[a][m] = z
                
        for a in authors:
            count = sum(1 for m in metrics if z_scores[a].get(m, 0.0) <= -1.5)
            if count >= 2:
                signals.append(a)
                
        return signals
