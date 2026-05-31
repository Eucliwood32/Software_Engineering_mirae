"""FR-5.2, FR-5.3 ReportExporter: .md/.csv/.html/.json 출력 (STR-7 판정 금지 용어 준수).

HTML/JSON은 운영 편의를 위한 확장 포맷이다(스펙 기본은 md/csv). HTML은 외부 CDN·웹폰트
없이 인라인 스타일만 사용하며(O-4 네트워크 0byte), JSON은 순수 표준 라이브러리로 직렬화한다.
"""
from __future__ import annotations
import csv
import html
import io
import json
from qce.model.types import MemberScore

_WARNING = "⚠ {source} 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다."


class ReportExporter:
    """FR-5.2 마크다운/CSV 생성. FR-5.3 결측 소스 경고 삽입."""

    def to_markdown(self, scores: list[MemberScore], missing: set[str] | None = None) -> str:
        """마크다운 테이블 + blockquote 경고. 헤더에 '종합 지표' 사용(STR-7)."""
        if missing is None:
            missing = set()

        lines = [
            "| 팀원 | 종합 지표 | Git 지표 | 문서 지표 | 메신저 지표 | Capping 적용 | 확인 필요 |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in sorted(scores, key=lambda s: s.total_score, reverse=True):
            lines.append(
                f"| {s.author} | {s.total_score:.4f} | {s.git_score:.4f} | "
                f"{s.doc_score:.4f} | {s.msg_score:.4f} | "
                f"{'O' if s.capping_applied else 'X'} | "
                f"{', '.join(s.signals) if s.signals else ''} |"
            )
        if missing:
            lines.append("")
            for src in sorted(missing):
                lines.append(f"> {_WARNING.format(source=src)}")
        return "\n".join(lines)

    def save(self, path: str, scores: list[MemberScore], missing: set[str] | None = None) -> None:
        """경로 확장자에 따라 포맷을 선택해 저장 (NFR-2.1: 쓰기는 이 메서드에 집중).
        .csv → CSV(BOM), .html → HTML, .json → JSON, 그 외 → Markdown."""
        lower = path.lower()
        if lower.endswith(".csv"):
            with open(path, "wb") as f:
                f.write(self.to_csv(scores, missing))
        elif lower.endswith(".html") or lower.endswith(".htm"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_html(scores, missing))
        elif lower.endswith(".json"):
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_json(scores, missing))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown(scores, missing))

    def to_csv(self, scores: list[MemberScore], missing: set[str] | None = None) -> bytes:
        """utf-8-sig(BOM) 인코딩. Excel 한글 호환."""
        if missing is None:
            missing = set()

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "팀원", "종합 지표", "Git 지표", "문서 지표", "메신저 지표",
            "Git 변경량(원시)", "문서 글자수(원시)", "메시지 발화(원시)",
            "Capping 적용", "확인 필요",
        ])
        for s in sorted(scores, key=lambda s: s.total_score, reverse=True):
            writer.writerow([
                s.author, s.total_score, s.git_score, s.doc_score, s.msg_score,
                s.raw_additions, s.raw_chars, s.raw_messages,
                "O" if s.capping_applied else "X",
                ", ".join(s.signals) if s.signals else "",
            ])
        if missing:
            writer.writerow([])
            for src in sorted(missing):
                writer.writerow(["WARNING", _WARNING.format(source=src)])
        return buf.getvalue().encode("utf-8-sig")

    def to_html(self, scores: list[MemberScore], missing: set[str] | None = None) -> str:
        """자기완결 HTML(인라인 스타일, 외부 리소스 없음). O-4 네트워크 0byte."""
        if missing is None:
            missing = set()

        def esc(v) -> str:
            return html.escape(str(v))

        rows = []
        for s in sorted(scores, key=lambda s: s.total_score, reverse=True):
            cap = "O" if s.capping_applied else "X"
            sig = esc(", ".join(s.signals)) if s.signals else ""
            rows.append(
                "<tr>"
                f"<td>{esc(s.author)}</td>"
                f"<td class='num'>{s.total_score:.4f}</td>"
                f"<td class='num'>{s.git_score:.4f}</td>"
                f"<td class='num'>{s.doc_score:.4f}</td>"
                f"<td class='num'>{s.msg_score:.4f}</td>"
                f"<td>{cap}</td><td>{sig}</td>"
                "</tr>"
            )
        warnings = "".join(
            f"<p class='warn'>{esc(_WARNING.format(source=src))}</p>"
            for src in sorted(missing)
        )
        style = (
            "body{font-family:sans-serif;margin:24px;color:#222}"
            "table{border-collapse:collapse;width:100%}"
            "th,td{border:1px solid #ccc;padding:6px 10px;text-align:left}"
            "th{background:#f2f2f2}.num{text-align:right;font-variant-numeric:tabular-nums}"
            ".warn{color:#b00020;background:#fff3f3;padding:8px;border-radius:4px}"
        )
        return (
            "<!DOCTYPE html><html lang='ko'><head><meta charset='utf-8'>"
            f"<title>QCE 기여도 리포트</title><style>{style}</style></head><body>"
            "<h1>QCE 기여도 리포트</h1>"
            "<table><thead><tr>"
            "<th>팀원</th><th>종합 지표</th><th>Git 지표</th><th>문서 지표</th>"
            "<th>메신저 지표</th><th>Capping 적용</th><th>확인 필요</th>"
            "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
            + warnings
            + "</body></html>"
        )

    def to_json(self, scores: list[MemberScore], missing: set[str] | None = None) -> str:
        """기계 판독용 JSON. 'members' 배열 + 'missing' 목록 + 경고 문구."""
        if missing is None:
            missing = set()
        payload = {
            "members": [
                {
                    "author": s.author,
                    "total_score": s.total_score,
                    "git_score": s.git_score,
                    "doc_score": s.doc_score,
                    "msg_score": s.msg_score,
                    "raw_additions": s.raw_additions,
                    "raw_chars": s.raw_chars,
                    "raw_messages": s.raw_messages,
                    "capping_applied": s.capping_applied,
                    "signals": list(s.signals),
                    "signal_details": list(s.signal_details),
                }
                for s in sorted(scores, key=lambda s: s.total_score, reverse=True)
            ],
            "missing": sorted(missing),
            "warnings": [_WARNING.format(source=src) for src in sorted(missing)],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
