from PyQt6.QtCore import QThread, pyqtSignal
from src.models.parsers.git_analyzer import GitAnalyzer
from src.models.parsers.document_parser import DocumentParser
from src.models.parsers.messenger_parser import MessengerParser
from src.models.parsers.stopword_filter import StopwordFilter


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
            # 1. Git parsing (FR-2.1)
            git_data = {}
            if self.git_path:
                stats_map = GitAnalyzer().analyze(self.git_path)
                for email, stats in stats_map.items():
                    git_data[email] = {
                        "total_commits": stats.commits,
                        "total_additions": stats.additions,
                        "total_deletions": stats.deletions,
                        "commits_list": stats.commits_list,
                    }

            # 2. OOXML parsing (FR-1.1, FR-1.2)
            doc_data = {}
            parser = DocumentParser()
            for path in self.doc_paths:
                for author, chars in parser.parse(path).items():
                    doc_data[author] = doc_data.get(author, 0) + chars

            # 3. Messenger parsing + stopword filtering (FR-3.1, FR-3.3)
            msg_data = {}
            if self.msg_path:
                parsed = MessengerParser().parse(self.msg_path)
                filtered = StopwordFilter().count_valid_messages(parsed.records)
                all_authors = {r.author for r in parsed.records}
                msg_data = {a: filtered.get(a, 0) for a in all_authors}

            self.finished.emit(git_data, doc_data, msg_data)

        except Exception as e:
            self.error.emit(str(e))
