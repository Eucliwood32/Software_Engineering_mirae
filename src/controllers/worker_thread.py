import os
import sys

# Ensure models can be imported when running from main.py or from within controllers
# Add src dir to sys path if not there
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from PyQt6.QtCore import QThread, pyqtSignal
from models.parsers.git_parser import parse_git_log
from models.parsers.ooxml_parser import parse_ooxml_file
from models.parsers.messenger_parser import parse_messenger_file

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict, dict, dict)
    error = pyqtSignal(str)
    
    def __init__(self, git_path, doc_paths, msg_path):
        super().__init__()
        self.git_path = git_path
        self.doc_paths = doc_paths
        self.msg_path = msg_path
        
    def run(self):
        try:
            # 1. Git parsing
            git_data = {}
            if self.git_path:
                git_data = parse_git_log(self.git_path)
                
            # 2. OOXML parsing
            doc_data = {}
            for path in self.doc_paths:
                res = parse_ooxml_file(path)
                for author, chars in res.items():
                    doc_data[author] = doc_data.get(author, 0) + chars
                    
            # 3. Messenger parsing
            msg_data = {}
            if self.msg_path:
                msg_data = parse_messenger_file(self.msg_path)
                
            self.finished.emit(git_data, doc_data, msg_data)
            
        except Exception as e:
            self.error.emit(str(e))
