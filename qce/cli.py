"""QCE 헤드리스(CLI) 분석 모드.

GUI 없이 동일한 분석 파이프라인(파싱 → 집계 → 리포트)을 실행한다. CI/배치 환경이나
스크립트에서 활용한다. PyQt에 의존하지 않으며(Qt import 없음) Model 컴포넌트만
재사용한다. 네트워크 통신을 하지 않는다(O-4).

사용 예:
  python -m qce --git ./repo --doc a.docx --doc b.pptx --msg chat.txt \
                --weights 0.5,0.3,0.2 --out report.md
  python -m qce --git ./repo --format csv --out report.csv
  python -m qce --git ./repo            # 표준출력에 표만 출력(--out 생략)
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from qce.model.business.contribution_aggregator import ContributionAggregator
from qce.model.business.report_exporter import ReportExporter
from qce.model.business.weight_preset_manager import WeightPresetManager
from qce.model.parsing.document_parser import DocumentParser
from qce.model.parsing.git_analyzer import GitAnalyzer
from qce.model.parsing.messenger_parser import MessengerParser
from qce.model.parsing.stopword_filter import StopwordFilter
from qce.model.types import MemberScore

_DEFAULT_WEIGHTS = {"git": 0.4, "doc": 0.4, "msg": 0.2}


# --------------------------------------------------------------------------- #
# 파이프라인 (Qt 비의존, 테스트 가능)
# --------------------------------------------------------------------------- #
def parse_weights(spec: Optional[str]) -> dict[str, float]:
    """'g,d,m' 또는 프리셋명 → {git,doc,msg}. None이면 기본 가중치."""
    mgr = WeightPresetManager()
    if not spec:
        return dict(_DEFAULT_WEIGHTS)
    if spec in mgr.PRESETS:
        return mgr.get_preset(spec)
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) != 3:
        raise ValueError("가중치는 'git,doc,msg' 3개 또는 프리셋명이어야 합니다.")
    try:
        g, d, m = (float(p) for p in parts)
    except ValueError as exc:
        raise ValueError(f"가중치 파싱 실패: {spec}") from exc
    if not mgr.validate_sum(g, d, m):
        # 합이 1.0이 아니면 비례 정규화해 진행(경고는 호출측 책임).
        return mgr.normalize({"git": g, "doc": d, "msg": m})
    return {"git": g, "doc": d, "msg": m}


def run_analysis(
    git_path: str = "",
    doc_paths: Optional[Sequence[str]] = None,
    msg_path: str = "",
    weights: Optional[dict[str, float]] = None,
) -> list[MemberScore]:
    """동기 분석 실행. 가용 소스만 집계(None 소스는 가중치 재조정)."""
    weights = weights or dict(_DEFAULT_WEIGHTS)

    doc_data: Optional[dict[str, int]] = None
    if doc_paths:
        doc_data = {}
        parser = DocumentParser()
        for path in doc_paths:
            for author, chars in parser.parse(path).items():
                doc_data[author] = doc_data.get(author, 0) + chars

    git_data = GitAnalyzer().analyze(git_path) if git_path else None

    msg_data: Optional[dict[str, int]] = None
    if msg_path:
        parsed = MessengerParser().parse(msg_path)
        filtered = StopwordFilter().count_valid_messages(parsed.records)
        all_authors = {r.author for r in parsed.records}
        msg_data = {a: filtered.get(a, 0) for a in all_authors}

    return ContributionAggregator().aggregate(
        git=git_data, docs=doc_data, msgs=msg_data, weights=weights
    )


def detect_missing(
    git_path: str, doc_paths: Optional[Sequence[str]], msg_path: str
) -> set[str]:
    """입력으로 주어지지 않은 소스를 결측으로 표시(리포트 경고용)."""
    missing: set[str] = set()
    if not git_path:
        missing.add("Git")
    if not doc_paths:
        missing.add("문서")
    if not msg_path:
        missing.add("메신저")
    return missing


# --------------------------------------------------------------------------- #
# 출력 포맷
# --------------------------------------------------------------------------- #
def render_text_table(scores: list[MemberScore]) -> str:
    """표준출력용 고정폭 텍스트 표."""
    if not scores:
        return "(분석 결과 없음)"
    header = f"{'팀원':<14}{'종합':>8}{'Git':>8}{'문서':>8}{'메신저':>8}  신호"
    lines = [header, "-" * len(header)]
    for s in sorted(scores, key=lambda x: x.total_score, reverse=True):
        flags = ",".join(s.signals) if s.signals else "-"
        lines.append(
            f"{s.author:<14}{s.total_score:>8.4f}{s.git_score:>8.4f}"
            f"{s.doc_score:>8.4f}{s.msg_score:>8.4f}  {flags}"
        )
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 엔트리포인트
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qce",
        description="QCE 팀기여도 정량평가 — 헤드리스 분석 (네트워크 미사용).",
    )
    p.add_argument("--git", default="", metavar="PATH", help="분석할 Git 저장소 경로")
    p.add_argument("--doc", action="append", default=[], metavar="FILE",
                   help="OOXML 문서(.docx/.pptx/.hwpx). 복수 지정 가능")
    p.add_argument("--msg", default="", metavar="FILE", help="메신저 내보내기 파일")
    p.add_argument("--weights", default=None, metavar="G,D,M",
                   help="가중치 'git,doc,msg' 또는 프리셋명(개발 중심/기획 중심/균형 설정)")
    p.add_argument("--out", default=None, metavar="PATH",
                   help="리포트 저장 경로(.md/.csv/.html/.json). 생략 시 표준출력만")
    p.add_argument("--format", default=None, choices=["md", "csv", "html", "json"],
                   help="출력 포맷 강제(미지정 시 --out 확장자로 추론)")
    return p


def _resolve_out_path(out: str, fmt: Optional[str]) -> str:
    """--format 지정 시 확장자를 맞춰준다."""
    if not fmt:
        return out
    base = out.rsplit(".", 1)[0] if "." in out else out
    return f"{base}.{fmt}"


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if not (args.git or args.doc or args.msg):
        print("오류: --git/--doc/--msg 중 최소 하나의 입력이 필요합니다.", file=sys.stderr)
        return 2

    try:
        weights = parse_weights(args.weights)
    except ValueError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 2

    scores = run_analysis(
        git_path=args.git, doc_paths=args.doc, msg_path=args.msg, weights=weights
    )
    missing = detect_missing(args.git, args.doc, args.msg)

    print(render_text_table(scores))

    if args.out:
        path = _resolve_out_path(args.out, args.format)
        try:
            ReportExporter().save(path, scores, missing)
            print(f"\n리포트 저장 완료: {path}")
        except Exception as exc:                       # noqa: BLE001 — CLI 경계
            print(f"오류: 리포트 저장 실패 ({exc})", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
