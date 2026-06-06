import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from qce.view.main_window import MainWindow
from qce.view.style import tokens as T
from qce.view.style.theme import theme_manager, MODE_DARK
from qce.controller.analysis_orchestrator import AnalysisOrchestrator
from qce.controller.app_controller import AppController

def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont(T.FONT_FAMILY, T.FONT_SIZE_BASE))  # 한글 폰트 명시(C-5)

    # README 스크린샷은 다크모드로 통일 (FR-5.8)
    theme_manager.set_mode(MODE_DARK)

    orchestrator = AnalysisOrchestrator()
    window = MainWindow()
    controller = AppController(window, orchestrator)

    window.resize(1280, 860)
    window.show()
    QApplication.processEvents()

    time.sleep(1)
    QApplication.processEvents()
    pixmap = window.grab()
    pixmap.save("qce_submit_screen.png")
    print(f"Submit screen saved. ({pixmap.width()}x{pixmap.height()})")

    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
    docs_dir = os.path.join(sample_dir, "docs")
    chat_file = os.path.join(sample_dir, "chat", "kakao_chat.txt")
    git_dir = os.path.join(sample_dir, "repo")

    submit_screen = window.submit

    submit_screen._handle_dropped_paths([docs_dir, chat_file, git_dir])
    QApplication.processEvents()

    # 가중치 프리셋(개발 중심)을 적용해야 합계 100% → [분석 시작] 버튼이 활성화된다
    submit_screen.analysis_panel.apply_preset("개발 중심")
    QApplication.processEvents()

    # Simulate clicking "분석 시작"
    submit_screen.analysis_panel._analyze_btn.click()

    def wait_and_capture():
        if window.stack.currentWidget() == window.result:
            time.sleep(2)
            QApplication.processEvents()

            # 차트 진입 애니메이션을 최종 프레임까지 즉시 진행해 그래프가 또렷하게 잡히도록
            dash = window.result.dashboard
            for chart in (dash.bar, dash.radar, dash.scatter):
                chart.finish_animation()
            QApplication.processEvents()

            res_pixmap = window.grab()
            res_pixmap.save("qce_result_screen.png")
            print(f"Result screen saved. ({res_pixmap.width()}x{res_pixmap.height()})")
            QApplication.quit()
        else:
            QTimer.singleShot(500, wait_and_capture)

    QTimer.singleShot(500, wait_and_capture)

    app.exec()

if __name__ == "__main__":
    run()
