from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QProgressBar, QGroupBox, QSlider, QStatusBar)
from PyQt6.QtCore import Qt
from .components.charts import ChartsView
from .components.anomaly_signal_panel import AnomalySignalPanel

class MainWindow(QMainWindow):
    """FR-5 대시보드 메인 윈도우"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QCE (부탁해 꼬마선장) - 종합 기여도 평가")
        self.resize(1100, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setFixedWidth(300)
        
        self._init_input_section()
        self._init_weight_section()
        self._init_control_section()
        
        self.left_layout.addStretch()
        self.main_layout.addWidget(self.left_panel)
        
        self.charts_view = ChartsView()
        self.main_layout.addWidget(self.charts_view, stretch=3)
        
        self.signal_panel = AnomalySignalPanel()
        self.signal_panel.setFixedWidth(280)
        self.main_layout.addWidget(self.signal_panel)
        
        # 경고 배너 (FR-5.3: 결측 데이터 경고)
        self.warning_banner = QLabel()
        self.warning_banner.setStyleSheet("background-color: #FFF9C4; padding: 8px; color: #333;")
        self.warning_banner.setWordWrap(True)
        self.warning_banner.setVisible(False)
        self.statusBar().addPermanentWidget(self.warning_banner, 1)
        
        self.status_bar = self.statusBar()
        
    def _init_input_section(self):
        group = QGroupBox("입력 데이터 설정")
        layout = QVBoxLayout(group)
        
        self.btn_git = QPushButton("Git 저장소 폴더 선택...")
        self.lbl_git = QLabel("선택 안됨")
        layout.addWidget(self.btn_git)
        layout.addWidget(self.lbl_git)
        
        self.btn_doc = QPushButton("문서(.pptx, .docx, .hwpx) 파일 선택...")
        self.lbl_doc = QLabel("0개 파일 선택됨")
        layout.addWidget(self.btn_doc)
        layout.addWidget(self.lbl_doc)
        
        self.btn_msg = QPushButton("메신저(카카오톡 .txt) 파일 선택...")
        self.lbl_msg = QLabel("선택 안됨")
        layout.addWidget(self.btn_msg)
        layout.addWidget(self.lbl_msg)
        
        self.left_layout.addWidget(group)
        
    def _init_weight_section(self):
        group = QGroupBox("가중치 설정 (합계 1.00)")
        layout = QVBoxLayout(group)
        
        preset_layout = QHBoxLayout()
        self.btn_preset_dev = QPushButton("개발 중심")
        self.btn_preset_pm = QPushButton("기획 중심")
        self.btn_preset_bal = QPushButton("균형 설정")
        preset_layout.addWidget(self.btn_preset_dev)
        preset_layout.addWidget(self.btn_preset_pm)
        preset_layout.addWidget(self.btn_preset_bal)
        layout.addLayout(preset_layout)
        
        def make_slider(name):
            lbl = QLabel(f"{name}: 0.00")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setSingleStep(5)
            layout.addWidget(lbl)
            layout.addWidget(slider)
            return slider, lbl
            
        self.slider_git, self.lbl_weight_git = make_slider("Git 가중치")
        self.slider_doc, self.lbl_weight_doc = make_slider("문서 가중치")
        self.slider_msg, self.lbl_weight_msg = make_slider("메신저 가중치")
        
        self.lbl_weight_warning = QLabel("")
        self.lbl_weight_warning.setStyleSheet("color: red;")
        layout.addWidget(self.lbl_weight_warning)
        
        self.left_layout.addWidget(group)
        
    def _init_control_section(self):
        group = QGroupBox("실행 및 결과")
        layout = QVBoxLayout(group)
        
        # FR-3.3: 불용어 사전 편집 UI는 제공하지 않는다 (ConOps §6.4)
        # 편집 버튼 삭제됨
        
        self.btn_analyze = QPushButton("분석 시작")
        self.btn_analyze.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(self.btn_analyze)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.btn_export = QPushButton("리포트 내보내기 (.md / .csv)")
        self.btn_export.setEnabled(False)
        layout.addWidget(self.btn_export)
        
        self.left_layout.addWidget(group)
        
    def show_progress(self, show: bool):
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)
            
    def set_analyzing_state(self, is_analyzing: bool):
        self.btn_analyze.setEnabled(not is_analyzing)
        self.show_progress(is_analyzing)
        
    def show_warning_banner(self, messages: list):
        """FR-5.3: 결측 데이터 경고 배너"""
        if messages:
            self.warning_banner.setText("\n".join(messages))
            self.warning_banner.setVisible(True)
        else:
            self.warning_banner.setVisible(False)
