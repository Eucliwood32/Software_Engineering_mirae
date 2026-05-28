from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame

class AnomalySignalPanel(QWidget):
    """
    FR-4.2, 4.2c: 이상 신호 알림 카드 및 정상 처리 UI
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)
        
        title_lbl = QLabel("<b>이상 신호 알림</b>")
        self.layout.addWidget(title_lbl)
        self.layout.addWidget(self.scroll_area)
        
    def add_signal_card(self, title: str, details: str, on_ignore_callback=None):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(f"<b>{title}</b>")
        title_label.setStyleSheet("color: red;")
        details_label = QLabel(details)
        details_label.setWordWrap(True)
        
        ignore_btn = QPushButton("정상으로 표시")
        if on_ignore_callback:
            def handler():
                on_ignore_callback()
                card.deleteLater()
            ignore_btn.clicked.connect(handler)
            
        card_layout.addWidget(title_label)
        card_layout.addWidget(details_label)
        card_layout.addWidget(ignore_btn)
        
        count = self.scroll_layout.count()
        self.scroll_layout.insertWidget(count - 1, card)
        
    def clear_signals(self):
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
