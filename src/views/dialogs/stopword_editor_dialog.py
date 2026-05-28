from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QInputDialog, QPushButton, QLabel

class StopwordEditorDialog(QDialog):
    """
    FR-3.3: 불용어 사전 편집 UI
    """
    def __init__(self, stopword_dict_obj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("불용어 사전 편집")
        self.resize(400, 300)
        self.stopword_obj = stopword_dict_obj
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("현재 등록된 불용어 목록:"))
        
        self.list_widget = QListWidget()
        self._populate_list()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self.add_word)
        remove_btn = QPushButton("삭제")
        remove_btn.clicked.connect(self.remove_word)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
    def _populate_list(self):
        self.list_widget.clear()
        for cat, words in self.stopword_obj.stopwords.items():
            for w in words:
                self.list_widget.addItem(f"[{cat}] {w}")
                
    def add_word(self):
        word, ok = QInputDialog.getText(self, "단어 추가", "추가할 불용어를 입력하세요:")
        if ok and word.strip():
            word = word.strip()
            cat = "사용자추가"
            if cat not in self.stopword_obj.stopwords:
                self.stopword_obj.stopwords[cat] = []
            if word not in self.stopword_obj.stopwords[cat]:
                self.stopword_obj.stopwords[cat].append(word)
                self.stopword_obj.save_stopwords()
                self._populate_list()
                
    def remove_word(self):
        current_item = self.list_widget.currentItem()
        if not current_item: return
        text = current_item.text()
        if "]" in text:
            cat = text.split("]")[0].replace("[", "").strip()
            word = text.split("]")[1].strip()
            if cat in self.stopword_obj.stopwords and word in self.stopword_obj.stopwords[cat]:
                self.stopword_obj.stopwords[cat].remove(word)
                self.stopword_obj.save_stopwords()
                self._populate_list()
