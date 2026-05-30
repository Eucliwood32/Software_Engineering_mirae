import sys
import os
import subprocess
import webbrowser
import traceback
import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

def global_exception_handler(exctype, value, tb):
    """전역 예외 처리기: 에러 발생 시 로그 파일에 기록"""
    log_path = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "qce_error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        traceback.print_exception(exctype, value, tb, file=f)
    
    # 기본 예외 처리기도 호출 (개발 환경 시 출력용)
    sys.__excepthook__(exctype, value, tb)
    
    # 팝업으로 알림 시도 (GUI가 이미 떠있는 상태라면)
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("치명적인 오류 발생")
        msg.setText(f"예상치 못한 오류가 발생했습니다.\n자세한 로그는 {log_path} 를 확인하세요.\n\n{str(value)}")
        msg.exec()
    except:
        pass

# Ensure src path is in sys.path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from views.main_window import MainWindow
from controllers.main_controller import MainController

def check_git_installed(parent_widget=None):
    """
    FR-2.2: Git 헬스체크
    """
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            stdin=subprocess.DEVNULL,
            timeout=5, 
            check=True,
            creationflags=creationflags
        )
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        msg = QMessageBox(parent_widget)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Git 설치 경고")
        msg.setText("Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.")
        msg.setInformativeText("이 앱의 Git 저장소 분석 기능을 사용하려면 Git이 필요합니다.<br>링크를 클릭하여 다운로드 하세요: <a href='https://git-scm.com/download/win'>https://git-scm.com/download/win</a><br>PATH 환경 변수를 반드시 확인해주세요.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setTextFormat(Qt.TextFormat.RichText)
        
        msg.exec()

def main():
    app = QApplication(sys.argv)
    
    # Apply basic style (Optional, but helps with Windows look)
    app.setStyle("Fusion")
    
    main_window = MainWindow()
    controller = MainController(main_window) # Keeps reference alive
    
    main_window.show()
    
    # 헬스체크 팝업 띄우기 (창이 뜬 직후 표시)
    check_git_installed(main_window)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    sys.excepthook = global_exception_handler
    try:
        main()
    except Exception as e:
        # main() 실행 조차 실패한 경우를 대비한 최후 방어선
        global_exception_handler(type(e), e, e.__traceback__)
