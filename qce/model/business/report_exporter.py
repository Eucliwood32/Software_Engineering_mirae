"""ReportExporter — FR-5.2/5.3 보고서 직렬화 (MD / CSV / HTML / JSON)."""
from __future__ import annotations

import csv
import html
import io
import json
import os
from typing import List, Optional, Set

from qce.model.types import MemberScore


class ReportExporter:
    WARNING_TEMPLATE = "⚠ {source} 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다."

    def to_markdown(self, scores: List[MemberScore], missing: Optional[Set[str]] = None) -> str:
        if missing is None:
            missing = set()
        sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)
        lines = [
            "| 팀원 | 종합 지표 | Git 지표 | 문서 지표 | 메신저 지표 | Capping 적용 | 확인 필요 |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in sorted_scores:
            capping = "O" if s.capping_applied else "X"
            anomaly = ", ".join(s.signals) if s.signals else ""
            lines.append(
                f"| {s.author} | {round(s.total_score,4)} | {round(s.git_score,4)} |"
                f" {round(s.doc_score,4)} | {round(s.msg_score,4)} | {capping} | {anomaly} |"
            )
        if missing:
            lines.append("")
            for source in sorted(missing):
                lines.append(f"> {self.WARNING_TEMPLATE.format(source=source)}")
        return "\n".join(lines)

    def to_csv(self, scores: List[MemberScore], missing: Optional[Set[str]] = None) -> bytes:
        if missing is None:
            missing = set()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "팀원", "종합 지표", "Git 지표", "문서 지표", "메신저 지표",
            "Git 변경량(원시)", "문서 글자수(원시)", "메시지 발화(원시)",
            "Capping 적용", "확인 필요",
        ])
        for s in sorted(scores, key=lambda x: x.total_score, reverse=True):
            writer.writerow([
                s.author, round(s.total_score, 4), round(s.git_score, 4),
                round(s.doc_score, 4), round(s.msg_score, 4),
                s.raw_additions, s.raw_chars, s.raw_messages,
                "O" if s.capping_applied else "X",
                ", ".join(s.signals) if s.signals else "",
            ])
        if missing:
            writer.writerow([])
            for source in sorted(missing):
                writer.writerow(["WARNING", self.WARNING_TEMPLATE.format(source=source)])
        return output.getvalue().encode("utf-8-sig")

    def to_html(self, scores: List[MemberScore], missing: Optional[Set[str]] = None) -> str:
        if missing is None:
            missing = set()
        sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)
        rows = ""
        for s in sorted_scores:
            author_escaped = html.escape(s.author)
            signals_escaped = html.escape(", ".join(s.signals)) if s.signals else ""
            rows += (
                f"<tr><td>{author_escaped}</td>"
                f"<td>{round(s.total_score,4)}</td>"
                f"<td>{round(s.git_score,4)}</td>"
                f"<td>{round(s.doc_score,4)}</td>"
                f"<td>{round(s.msg_score,4)}</td>"
                f"<td>{'O' if s.capping_applied else 'X'}</td>"
                f"<td>{signals_escaped}</td></tr>\n"
            )
        warnings = ""
        if missing:
            warn_items = "".join(
                f'<li class="warn">{html.escape(self.WARNING_TEMPLATE.format(source=s))}</li>'
                for s in sorted(missing)
            )
            warnings = f"<ul>{warn_items}</ul>"
        return (
            "<!DOCTYPE html>\n<html lang='ko'><head><meta charset='UTF-8'>"
            "<title>QCE 리포트</title></head><body>\n"
            "<table>\n"
            "<thead><tr><th>팀원</th><th>종합 지표</th><th>Git 지표</th>"
            "<th>문서 지표</th><th>메신저 지표</th><th>Capping</th><th>확인 필요</th></tr></thead>\n"
            f"<tbody>\n{rows}</tbody>\n</table>\n"
            f"{warnings}\n</body></html>"
        )

    def to_json(self, scores: List[MemberScore], missing: Optional[Set[str]] = None) -> str:
        if missing is None:
            missing = set()
        sorted_scores = sorted(scores, key=lambda x: x.total_score, reverse=True)
        members = [
            {
                "author": s.author,
                "total_score": round(s.total_score, 4),
                "git_score": round(s.git_score, 4),
                "doc_score": round(s.doc_score, 4),
                "msg_score": round(s.msg_score, 4),
                "capping_applied": s.capping_applied,
                "signals": list(s.signals),
            }
            for s in sorted_scores
        ]
        missing_list = sorted(missing)
        warnings = [self.WARNING_TEMPLATE.format(source=src) for src in missing_list]
        return json.dumps(
            {"members": members, "missing": missing_list, "warnings": warnings},
            ensure_ascii=False, indent=2,
        )

    def save(self, path: str, scores: List[MemberScore], missing: Optional[Set[str]] = None) -> None:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            with open(path, "wb") as f:
                f.write(self.to_csv(scores, missing))
        elif ext == ".html":
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_html(scores, missing))
        elif ext == ".json":
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_json(scores, missing))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.to_markdown(scores, missing))


__all__ = ["ReportExporter"]
