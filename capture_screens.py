import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from qce.view.main_window import MainWindow
from qce.controller.analysis_orchestrator import AnalysisOrchestrator
from qce.controller.app_controller import AppController

def run():
    app = QApplication(sys.argv)
    
    orchestrator = AnalysisOrchestrator()
    window = MainWindow()
    controller = AppController(window, orchestrator)
    
    window.show()
    QApplication.processEvents()
    
    time.sleep(1)
    QApplication.processEvents()
    pixmap = window.grab()
    pixmap.save("qce_submit_screen.png")
    print("Submit screen saved.")
    
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")
    docs_dir = os.path.join(sample_dir, "docs")
    chat_file = os.path.join(sample_dir, "chat", "kakao_chat.txt")
    git_dir = os.path.join(sample_dir, "repo")
    
    submit_screen = window.submit
    
    submit_screen._handle_dropped_paths([docs_dir, chat_file, git_dir])
    QApplication.processEvents()
    
    # Simulate clicking "분석 시작"
    submit_screen.analysis_panel._analyze_btn.click()
    
    def wait_and_capture():
        if window.stack.currentWidget() == window.result:
            time.sleep(2)
            QApplication.processEvents()
            
            res_pixmap = window.grab()
            res_pixmap.save("qce_result_screen.png")
            print("Result screen saved.")
            QApplication.quit()
        else:
            QTimer.singleShot(500, wait_and_capture)
            
    QTimer.singleShot(500, wait_and_capture)
    
    app.exec()

if __name__ == "__main__":
    run()
