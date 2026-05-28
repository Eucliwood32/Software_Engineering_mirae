from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt

class AliasMappingDialog(QDialog):
    """
    FR-1.3: 식별자 매핑 다이얼로그
    """
    def __init__(self, aliases: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("팀원 식별자 매핑")
        self.resize(500, 400)
        self.aliases = list(aliases)
        self.mapping_result = {}
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("분석된 식별자를 실제 팀원 이름으로 매핑해주세요."))
        
        self.table = QTableWidget(len(self.aliases), 2)
        self.table.setHorizontalHeaderLabels(["추출된 식별자", "매핑할 팀원"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        self.combo_boxes = []
        
        for i, alias in enumerate(self.aliases):
            item = QTableWidgetItem(alias)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item)
            
            combo = QComboBox()
            combo.setEditable(True)
            combo.addItems(["(미매핑)", alias])
            self.table.setCellWidget(i, 1, combo)
            self.combo_boxes.append(combo)
            
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장 및 분석 계속")
        save_btn.clicked.connect(self.accept_mapping)
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
    def accept_mapping(self):
        self.mapping_result = {}
        for i, alias in enumerate(self.aliases):
            combo = self.combo_boxes[i]
            target = combo.currentText().strip()
            if target and target != "(미매핑)":
                self.mapping_result[alias] = target
                
        if not self.mapping_result:
            QMessageBox.warning(self, "경고", "최소 1개 이상의 식별자를 매핑해야 합니다.")
            return
            
        self.accept()
