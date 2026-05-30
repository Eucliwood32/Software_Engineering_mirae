"""FR-5.2, FR-5.3 ReportExporter: .md/.csv 출력 (STR-7 판정 금지 용어 준수)."""
from __future__ import annotations
import csv
import io
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
        """경로 확장자에 따라 .csv 또는 .md로 저장 (NFR-2.1: 쓰기는 이 메서드에 집중)."""
        if path.endswith(".csv"):
            with open(path, "wb") as f:
                f.write(self.to_csv(scores, missing))
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
