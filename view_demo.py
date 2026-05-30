"""
View 미리보기 데모 — Controller/Model 파이프라인 없이 View 레이어만 띄운다.

샘플 점수 dict(§5.3 스키마)를 주입해 막대·레이더·산점도, 결측 배너, 가중치 패널,
Drag&Drop 셸을 시각 확인한다. 실제 앱에서는 이 데이터 흐름을 Controller가 채운다.

사용법
------
  # 데스크톱에 창 띄우기 (일반 터미널, 화면 필요)
  python view_demo.py

  # 화면 없이 PNG 스크린샷만 저장 (헤드리스/CI)
  set QT_QPA_PLATFORM=offscreen   (PowerShell: $env:QT_QPA_PLATFORM="offscreen")
  python view_demo.py --shot view_preview.png
"""
from __future__ import annotations

import argparse
import dataclasses
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from qce.model.types import MemberScore           # dataclass만 사용(무거운 의존 없음)
from qce.view.contract import SRC_MSG
from qce.view.main_window import MainWindow
from qce.view.style import tokens as T


def sample_score_dicts() -> list[dict]:
    """Controller가 push할 형태와 동일한 dict 목록(asdict로 직렬화)."""
    members = [
        MemberScore("조원희", 0.30, 0.20, 0.40, 0.28, 800, 1500, 120, False, []),
        MemberScore("이대한", 0.55, 0.10, 0.30, 0.31, 1000, 400, 90, True, ["EW-01"]),
        MemberScore("김휘중", 0.40, 0.45, 0.20, 0.29, 600, 2000, 50, False, []),
        MemberScore("D팀원", 0.05, 0.08, 0.05, 0.12, 50, 200, 10, False, ["ZSCORE"]),
    ]
    return [dataclasses.asdict(m) for m in members]


def _wire_demo(win: MainWindow, scores: list[dict], missing: set[str]) -> None:
    """데모용 임시 배선: 제출→로딩→결과 3-스크린 흐름. (실제로는 Controller가 수행)"""
    def run() -> None:
        win.show_loading()
        win.loading.start()
        win.loading.set_value(100)
        win.result.render(scores, missing)
        win.loading.finish()
        win.show_result()
        win.flash_status("데모 분석 완료 (샘플 데이터)", 4000)

    win.submit.analysis_panel.analyze_clicked.connect(run)
    win.submit.analysis_panel.apply_preset("개발 중심")
    win.result.new_analysis_requested.connect(win.show_submit)
    win.result.merge_requested.connect(
        lambda m: win.flash_status(f"병합 요청(데모, 재집계는 Controller 몫): {m}", 5000)
    )
    run()  # 기동 직후 한 번 분석해 결과 화면을 보여준다


def _finish_animations(win: MainWindow) -> None:
    dash = win.result.dashboard
    for chart in (dash.bar, dash.radar, dash.scatter):
        chart.finish_animation()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="QCE View 미리보기 데모")
    parser.add_argument("--shot", metavar="PATH", help="오프스크린 렌더 후 PNG로 저장하고 종료")
    parser.add_argument("--missing-msg", action="store_true",
                        help="메신저 소스 결측 시나리오(배너+점선 표시)로 렌더")
    parser.add_argument("--screen", choices=["submit", "loading", "result"], default="result",
                        help="--shot 캡처 대상 화면 (기본: result)")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv[:1])
    app.setFont(QFont(T.FONT_FAMILY, T.FONT_SIZE_BASE))   # 한글 폰트 명시(C-5)
    win = MainWindow()
    win.resize(1280, 860)

    missing: set[str] = {SRC_MSG} if args.missing_msg else set()
    _wire_demo(win, sample_score_dicts(), missing)

    if args.shot:
        win.show()
        app.processEvents()
        _finish_animations(win)
        {"submit": win.show_submit, "loading": win.show_loading, "result": win.show_result}[args.screen]()
        app.processEvents()
        pixmap = win.grab()
        pixmap.save(args.shot)
        print(f"saved screenshot -> {args.shot} ({pixmap.width()}x{pixmap.height()})")
        return 0

    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
