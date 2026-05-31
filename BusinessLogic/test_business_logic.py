"""
test_business_logic.py

BusinessLogic.py의 9개 클래스에 대한 단위 테스트.
기준 문서: docs/03-verification-validation/test-cases.md v1.3
"""

import math
import os
import sys
import importlib.util
import pytest

# BusinessLogic 모듈을 직접 로드 (패키지 구조 없이)
_bl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BusinessLogic.py")
_spec = importlib.util.spec_from_file_location("BusinessLogic", _bl_path)
_bl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bl)

CommitStats = _bl.CommitStats
MemberScore = _bl.MemberScore
Normalizer = _bl.Normalizer
CappingScaler = _bl.CappingScaler
AnomalySignalDetector = _bl.AnomalySignalDetector
WeightPresetManager = _bl.WeightPresetManager
WeightRebalancer = _bl.WeightRebalancer
AliasMapper = _bl.AliasMapper
ContributionAggregator = _bl.ContributionAggregator
CacheManager = _bl.CacheManager
ReportExporter = _bl.ReportExporter
NormalizedSignalsTracker = _bl.NormalizedSignalsTracker
AliasExtractor = _bl.AliasExtractor


def sample_scores(n: int) -> list:
    names = ["A팀원", "B팀원", "C팀원", "D팀원"][:n]
    scores_data = [
        (0.9, 0.8, 0.7),
        (0.7, 0.6, 0.8),
        (0.8, 0.9, 0.6),
        (0.05, 0.05, 0.05),
    ]
    result = []
    for i, name in enumerate(names):
        g, d, m = scores_data[i]
        result.append(MemberScore(
            author=name,
            git_score=g, doc_score=d, msg_score=m,
            total_score=round(g * 0.4 + d * 0.4 + m * 0.2, 4),
            raw_additions=100 * (i + 1),
            raw_chars=200 * (i + 1),
            raw_messages=50 * (i + 1),
            capping_applied=False,
            signals=[],
            signal_details=[],
            commit_dates=[]
        ))
    return result


class TestNormalizer:
    def setup_method(self):
        self.norm = Normalizer()

    def test_basic_normalize(self):
        assert self.norm.normalize([0, 50, 100]) == [0.0, 0.5, 1.0]

    def test_zero_variance(self):
        result = self.norm.normalize([75, 75, 75])
        assert result == [0.5, 0.5, 0.5]

    def test_range_0_to_1(self):
        result = self.norm.normalize([10, 200, 50, 3000, 1])
        for v in result:
            assert 0.0 <= v <= 1.0

    def test_two_elements(self):
        assert self.norm.normalize([1, 2]) == [0.0, 1.0]

    def test_round_4_digits(self):
        result = self.norm.normalize([10, 20, 30, 40])
        for v in result:
            assert v == round(v, 4)

    def test_empty_input(self):
        assert self.norm.normalize([]) == []


class TestCappingScaler:
    def setup_method(self):
        self.cs = CappingScaler()

    def test_cap_over_threshold(self):
        assert self.cs.cap(5000) == (1000, True)

    def test_cap_under_threshold(self):
        assert self.cs.cap(999) == (999, False)

    def test_cap_at_boundary(self):
        assert self.cs.cap(1000) == (1000, False)

    def test_cap_just_above_boundary(self):
        assert self.cs.cap(1001) == (1000, True)

    def test_log_scale_zero(self):
        assert self.cs.log_scale(0) == 0.0

    def test_log_scale_positive(self):
        result = self.cs.log_scale(100)
        assert abs(result - math.log1p(100)) < 0.01


class TestAnomalyFrequency:
    def setup_method(self):
        self.detector = AnomalySignalDetector()

    def test_frequency_burst(self):
        repo = {
            "Alice": CommitStats(
                commits=10, additions=0, deletions=0,
                commits_list=[
                    {"date": "2026-01-01"}, {"date": "2026-01-02"}, {"date": "2026-01-03"},
                    {"date": "2026-01-04"}, {"date": "2026-01-05"}, {"date": "2026-01-06"},
                    {"date": "2026-01-07"}, {"date": "2026-01-08"}, {"date": "2026-01-09"},
                ] + [{"date": "2026-01-10"}] * 10
            )
        }
        signals = self.detector.detect_frequency(repo)
        assert len(signals) >= 1
        assert signals[0]["author"] == "Alice"

    def test_frequency_signal_fields(self):
        repo = {
            "Bob": CommitStats(
                commits=38, additions=0, deletions=0,
                commits_list=[
                    {"date": "2026-01-01"}, {"date": "2026-01-02"}, {"date": "2026-01-03"},
                    {"date": "2026-01-04"}, {"date": "2026-01-05"}, {"date": "2026-01-06"},
                    {"date": "2026-01-07"}, {"date": "2026-01-08"}, {"date": "2026-01-09"},
                ] + [{"date": "2026-01-10"}] * 30
            )
        }
        signals = self.detector.detect_frequency(repo)
        assert len(signals) >= 1
        sig = signals[0]
        assert "author" in sig
        assert "period" in sig
        assert "period_commits" in sig
        assert "baseline_avg" in sig

    def test_frequency_no_burst(self):
        repo = {
            "Carol": CommitStats(
                commits=6, additions=0, deletions=0,
                commits_list=[
                    {"date": "2026-01-01"}, {"date": "2026-01-01"},
                    {"date": "2026-01-02"}, {"date": "2026-01-02"},
                    {"date": "2026-01-03"}, {"date": "2026-01-03"},
                ]
            )
        }
        signals = self.detector.detect_frequency(repo)
        assert len(signals) == 0


class TestAnomalyZScore:
    def setup_method(self):
        self.detector = AnomalySignalDetector()

    def test_zscore_two_low_axes(self):
        scores = sample_scores(4)
        flagged = self.detector.detect_zscore(scores)
        assert "D팀원" in flagged

    def test_zscore_one_low_axis(self):
        scores = [
            MemberScore("A", 0.8, 0.8, 0.8, 0.8, 100, 100, 100, False, []),
            MemberScore("B", 0.7, 0.7, 0.7, 0.7, 100, 100, 100, False, []),
            MemberScore("C", 0.6, 0.6, 0.6, 0.6, 100, 100, 100, False, []),
            MemberScore("D", 0.1, 0.6, 0.6, 0.4, 100, 100, 100, False, []),
        ]
        flagged = self.detector.detect_zscore(scores)
        assert "D" not in flagged

    def test_zscore_empty_input(self):
        assert self.detector.detect_zscore([]) == []


class TestWeightPresetManager:
    def setup_method(self):
        self.wpm = WeightPresetManager()

    def test_preset_dev(self):
        assert self.wpm.PRESETS["개발 중심"] == (0.60, 0.25, 0.15)

    def test_preset_planning(self):
        assert self.wpm.PRESETS["기획 중심"] == (0.20, 0.60, 0.20)

    def test_preset_balanced(self):
        assert self.wpm.PRESETS["균형 설정"] == (0.40, 0.40, 0.20)

    def test_validate_sum_false(self):
        assert self.wpm.validate_sum(0.5, 0.5, 0.5) is False

    def test_validate_sum_true(self):
        assert self.wpm.validate_sum(0.4, 0.4, 0.2) is True
        
    def test_normalize(self):
        out = self.wpm.normalize({"git": 4.0, "doc": 4.0, "msg": 2.0})
        assert abs(out["git"] - 0.4) < 1e-4
        assert abs(out["doc"] - 0.4) < 1e-4
        assert abs(out["msg"] - 0.2) < 1e-4
        
    def test_redistribute(self):
        current = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        out = self.wpm.redistribute("git", 0.7, current)
        assert abs(out["git"] - 0.7) < 1e-4
        assert abs(sum(out.values()) - 1.0) < 1e-4
        assert abs(out["doc"] / max(out["msg"], 1e-9) - 2.0) < 1e-1
        
    def test_match_preset(self):
        assert self.wpm.match_preset(0.4, 0.4, 0.2) == "균형 설정"
        assert self.wpm.match_preset(0.4, 0.4, 0.21) is None


class TestWeightRebalancer:
    def setup_method(self):
        self.wr = WeightRebalancer()
        self.weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}

    def test_rebalance_missing_msg(self):
        out = self.wr.rebalance(self.weights, available={"git", "doc"})
        assert abs(out["git"] - 0.5) < 1e-4
        assert abs(out["doc"] - 0.5) < 1e-4
        assert out["msg"] == 0.0
        assert abs(sum(out.values()) - 1.0) < 1e-4

    def test_rebalance_missing_git(self):
        out = self.wr.rebalance(self.weights, available={"doc", "msg"})
        assert out["git"] == 0.0
        assert abs(sum(out.values()) - 1.0) < 1e-4

    def test_rebalance_missing_doc(self):
        out = self.wr.rebalance(self.weights, available={"git", "msg"})
        assert out["doc"] == 0.0
        assert abs(sum(out.values()) - 1.0) < 1e-4

    def test_single_source(self):
        out = self.wr.rebalance(self.weights, available={"git"})
        assert abs(out["git"] - 1.0) < 1e-4
        assert out["doc"] == 0.0
        assert out["msg"] == 0.0

    def test_deterministic(self):
        r1 = self.wr.rebalance(self.weights, available={"git", "doc"})
        r2 = self.wr.rebalance(self.weights, available={"git", "doc"})
        assert r1 == r2

    def test_all_missing_raises(self):
        with pytest.raises(ValueError, match="분석 가능한 데이터 소스가 없습니다"):
            self.wr.rebalance(self.weights, available=set())


class TestAliasMapper:
    def setup_method(self):
        self.mapper = AliasMapper()

    def test_n_to_1_merge(self):
        raw = {"dh-lee": {"add": 10}, "daehan.lee": {"add": 5}, "이대한": {"add": 3}}
        mapping = {"dh-lee": "이대한", "daehan.lee": "이대한", "이대한": "이대한"}
        out = self.mapper.merge(raw, mapping)
        assert out["이대한"]["add"] == 18 and len(out) == 1

    def test_unmapped_excluded(self):
        raw = {"a": {"add": 1}, "ghost1": {"add": 9}, "ghost2": {"add": 7}}
        out = self.mapper.merge(raw, {"a": "Alice"})
        assert "Alice" in out
        assert "ghost1" not in out
        assert "ghost2" not in out

    def test_unknown_vs_unmapped(self):
        raw = {
            "Unknown": {"chars": 50},
            "ghost": {"chars": 30},
            "alice@test.com": {"chars": 100},
        }
        mapping = {
            "Unknown": "Unknown",
            "alice@test.com": "Alice",
        }
        out = self.mapper.merge(raw, mapping)
        assert "Unknown" in out
        assert "Alice" in out
        assert "ghost" not in out
        assert len(out) == 2


class TestContributionAggregator:
    def setup_method(self):
        self.agg = ContributionAggregator()

    def test_deterministic(self):
        git = {"A": CommitStats(3, 100, 10), "B": CommitStats(5, 200, 20)}
        docs = {"A": 500, "B": 300}
        msgs = {"A": 10, "B": 20}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}

        r1 = self.agg.aggregate(git, docs, msgs, weights)
        r2 = self.agg.aggregate(git, docs, msgs, weights)
        
        for s1, s2 in zip(r1, r2):
            assert s1.author == s2.author
            assert s1.total_score == s2.total_score
            assert s1.git_score == s2.git_score
            assert s1.doc_score == s2.doc_score
            assert s1.msg_score == s2.msg_score

    def test_single_source_only(self):
        docs = {"A": 100, "B": 200}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        result = self.agg.aggregate(git=None, docs=docs, msgs=None, weights=weights)
        
        for s in result:
            assert abs(s.total_score - s.doc_score) < 1e-4

    def test_git_none_docs_msgs_present(self):
        docs = {"A": 100}
        msgs = {"A": 5}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        result = self.agg.aggregate(git=None, docs=docs, msgs=msgs, weights=weights)
        assert len(result) == 1
        assert result[0].author == "A"

    def test_all_sources_present(self):
        git = {"A": CommitStats(5, 500, 50), "B": CommitStats(3, 100, 10)}
        docs = {"A": 300, "B": 600}
        msgs = {"A": 20, "B": 10}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        result = self.agg.aggregate(git, docs, msgs, weights)
        assert len(result) == 2
        for s in result:
            assert 0.0 <= s.total_score <= 1.0

    def test_capping_applied_flag(self):
        git = {"A": CommitStats(1, 5000, 0, [{"hash": "abcdefg", "date": "2026-01-01", "additions": 5000}])}
        docs = {"A": 100}
        msgs = {"A": 5}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        result = self.agg.aggregate(git, docs, msgs, weights)
        assert result[0].capping_applied is True
        assert "CAPPING" in result[0].signals

    def test_missing_source_different_score(self):
        git = {"A": CommitStats(3, 100, 10), "B": CommitStats(5, 200, 20)}
        docs = {"A": 300, "B": 500}
        msgs = {"A": 10, "B": 20}
        weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        
        with_msgs = self.agg.aggregate(git, docs, msgs, weights)
        without_msgs = self.agg.aggregate(git, docs, None, weights)


class TestCacheManager:
    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cm = CacheManager()
        data = {"scores": {"A": 0.3}, "ts": "2026-01-01T00:00"}
        cm.save(data)
        loaded = cm.load()
        assert loaded == data

    def test_corrupt_cache_recovers(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with open(".qce_cache", "w") as f:
            f.write("{not json")
        cm = CacheManager()
        out = cm.load()
        assert out == {}
        assert not os.path.exists(".qce_cache")

    def test_atomic_no_tmp_left(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cm = CacheManager()
        cm.save({"scores": {"A": 0.3}, "ts": "2026-01-01T00:00"})
        assert not os.path.exists(".qce_cache.tmp")
        assert os.path.exists(".qce_cache")

    def test_load_nonexistent(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cm = CacheManager()
        assert cm.load() == {}


class TestReportExporter:
    def setup_method(self):
        self.exporter = ReportExporter()
        self.scores = sample_scores(2)

    def test_markdown_table_structure(self):
        md = self.exporter.to_markdown(self.scores, missing=set())
        lines = md.split("\n")
        assert "|" in lines[0]
        assert "---" in lines[1]
        assert len(lines) >= 4

    def test_csv_has_bom(self):
        data = self.exporter.to_csv(self.scores, missing=set())
        assert data[:3] == b"\xef\xbb\xbf"

    def test_csv_korean_author(self):
        korean_scores = [
            MemberScore("김철수", 0.8, 0.7, 0.6, 0.72, 100, 200, 30, False, []),
            MemberScore("이영희", 0.5, 0.9, 0.4, 0.64, 50, 400, 20, False, []),
        ]
        data = self.exporter.to_csv(korean_scores, missing=set())
        decoded = data.decode("utf-8-sig")
        assert "김철수" in decoded
        assert "이영희" in decoded

    def test_no_verdict_wording_md(self):
        md = self.exporter.to_markdown(self.scores, missing=set())
        assert "최종 평가" not in md
        assert "종합 지표" in md or "종합" in md

    def test_no_verdict_wording_csv(self):
        data = self.exporter.to_csv(self.scores, missing=set())
        decoded = data.decode("utf-8-sig")
        assert "최종 평가" not in decoded
        assert "종합 지표" in decoded or "종합" in decoded


class TestReportExporterMissing:
    def setup_method(self):
        self.exporter = ReportExporter()
        self.scores = sample_scores(2)

    def test_md_missing_messenger(self):
        md = self.exporter.to_markdown(self.scores, missing={"메신저"})
        assert ">" in md
        assert "메신저" in md
        assert "제외되었습니다" in md

    def test_csv_missing_messenger(self):
        data = self.exporter.to_csv(self.scores, missing={"메신저"})
        decoded = data.decode("utf-8-sig")
        assert "WARNING" in decoded
        assert "메신저" in decoded

    def test_multiple_missing(self):
        md = self.exporter.to_markdown(self.scores, missing={"Git", "메신저"})
        assert "Git" in md
        assert "메신저" in md
        blockquotes = [l for l in md.split("\n") if l.startswith(">")]
        assert len(blockquotes) >= 2

    def test_no_missing_no_warning(self):
        md = self.exporter.to_markdown(self.scores, missing=set())
        assert ">" not in md
        assert "WARNING" not in md
        
        csv_data = self.exporter.to_csv(self.scores, missing=set())
        decoded = csv_data.decode("utf-8-sig")
        assert "WARNING" not in decoded

class TestNormalizedSignalsTracker:
    def setup_method(self):
        self.tracker = NormalizedSignalsTracker()
        
    def test_dismiss_and_restore(self):
        self.tracker.dismiss("Alice", "CAPPING", "hash123")
        assert self.tracker.is_dismissed("Alice", "CAPPING", "hash123")
        self.tracker.restore("Alice", "CAPPING", "hash123")
        assert not self.tracker.is_dismissed("Alice", "CAPPING", "hash123")

class TestAliasExtractor:
    def setup_method(self):
        self.extractor = AliasExtractor()
        
    def test_normalize_key(self):
        assert self.extractor.normalize_key("DH-Lee") == "dhlee"
        assert self.extractor.normalize_key("dh.lee@test.com") == "dhlee"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
