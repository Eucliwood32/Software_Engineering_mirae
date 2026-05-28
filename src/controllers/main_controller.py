import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog
from views.main_window import MainWindow
from views.dialogs.alias_mapping_dialog import AliasMappingDialog
from models.analysis.alias_extractor import AliasExtractor
from models.analysis.stopword_dictionary import StopwordDictionary
from models.analysis.detectors import Detectors, FrequencyAnomalyDetector, ZScoreAnomalyDetector
from models.analysis.aggregator import ContributionAggregator
from .worker_thread import AnalysisWorker

class MainController:
    """
    Controller 계층: View ↔ Model 중재.
    C-4: View에서 Model을 직접 import하지 않고, Controller가 중재한다.
    NFR-1.2: 중복 실행 방지 (Race Condition Guard).
    """
    def __init__(self, view: MainWindow):
        self.view = view
        self.stopword_dict = StopwordDictionary()
        
        self.git_path = ""
        self.doc_paths = []
        self.msg_path = ""
        self.is_analyzing = False
        
        self.cache_file = ".qce_cache"
        self._bind_events()
        self._load_cache()
        
    def _bind_events(self):
        self.view.btn_git.clicked.connect(self._select_git)
        self.view.btn_doc.clicked.connect(self._select_doc)
        self.view.btn_msg.clicked.connect(self._select_msg)
        
        self.view.btn_preset_dev.clicked.connect(lambda: self._set_weights(60, 25, 15))
        self.view.btn_preset_pm.clicked.connect(lambda: self._set_weights(20, 60, 20))
        self.view.btn_preset_bal.clicked.connect(lambda: self._set_weights(40, 40, 20))
        
        self.view.slider_git.valueChanged.connect(self._on_weight_change)
        self.view.slider_doc.valueChanged.connect(self._on_weight_change)
        self.view.slider_msg.valueChanged.connect(self._on_weight_change)
        
        # FR-3.3: 불용어 사전 편집 UI 없음 — 버튼 바인딩 삭제
        self.view.btn_analyze.clicked.connect(self._start_analysis)
        self.view.btn_export.clicked.connect(self._export_report)
        
        self._set_weights(40, 40, 20)
        
    def _set_weights(self, g, d, m):
        self.view.slider_git.setValue(g)
        self.view.slider_doc.setValue(d)
        self.view.slider_msg.setValue(m)
        
    def _on_weight_change(self):
        g = self.view.slider_git.value() / 100.0
        d = self.view.slider_doc.value() / 100.0
        m = self.view.slider_msg.value() / 100.0
        
        self.view.lbl_weight_git.setText(f"Git 가중치: {g:.2f}")
        self.view.lbl_weight_doc.setText(f"문서 가중치: {d:.2f}")
        self.view.lbl_weight_msg.setText(f"메신저 가중치: {m:.2f}")
        
        total = round(g + d + m, 2)
        if total != 1.00:
            self.view.btn_analyze.setEnabled(False)
            self.view.lbl_weight_warning.setText(
                f"가중치 합계가 1.00이어야 합니다. 현재: {total:.2f}")
        else:
            self.view.btn_analyze.setEnabled(not self.is_analyzing)
            self.view.lbl_weight_warning.setText("")
            
    def _select_git(self):
        path = QFileDialog.getExistingDirectory(self.view, "Git 저장소 폴더 선택")
        if path:
            self.git_path = path
            self.view.lbl_git.setText(os.path.basename(path))
            
    def _select_doc(self):
        # FR-1.1: .hwpx 추가
        paths, _ = QFileDialog.getOpenFileNames(
            self.view, "문서 파일 선택", "", 
            "문서 파일 (*.pptx *.docx *.hwpx)")
        if paths:
            self.doc_paths = paths
            self.view.lbl_doc.setText(f"{len(paths)}개 파일 선택됨")
            
    def _select_msg(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view, "메신저 파일 선택", "", "카카오톡 텍스트 (*.txt)")
        if path:
            self.msg_path = path
            self.view.lbl_msg.setText(os.path.basename(path))
        
    def _start_analysis(self):
        """NFR-1.2: 중복 실행 방지, FR-4.3: 모든 소스 부재 시 차단"""
        if self.is_analyzing: return
        
        # FR-4.3: 3개 소스 모두 부재 시 차단
        if not self.git_path and not self.doc_paths and not self.msg_path:
            QMessageBox.warning(
                self.view, "알림", 
                "분석 가능한 데이터 소스가 없습니다.\n"
                "Git 저장소, 문서 파일, 메신저 파일 중 최소 1개를 선택해주세요.")
            return
            
        self.is_analyzing = True
        self.view.set_analyzing_state(True)
        self.view.signal_panel.clear_signals()
        self.view.show_warning_banner([])  # 이전 경고 초기화
        
        self.worker = AnalysisWorker(self.git_path, self.doc_paths, self.msg_path)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.error.connect(self._on_worker_error)
        self.worker.start()
        
    def _on_worker_error(self, err_msg):
        self.is_analyzing = False
        self.view.set_analyzing_state(False)
        QMessageBox.critical(self.view, "오류", f"분석 중 오류 발생:\n{err_msg}")
        
    def _on_worker_finished(self, git_data, doc_data, msg_data):
        self.is_analyzing = False
        self.view.set_analyzing_state(False)
        
        aliases = AliasExtractor.extract_all_aliases(git_data, doc_data, msg_data)
        if not aliases:
            QMessageBox.information(self.view, "알림", "분석된 기여 데이터가 없습니다.")
            return
            
        dlg = AliasMappingDialog(list(aliases), self.view)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
            
        mapping = dlg.mapping_result
        
        # FR-4.2: Capping 적용
        capped_git, cap_signals = Detectors.apply_capping(git_data)
        freq_signals = FrequencyAnomalyDetector.detect(git_data)
        
        for sig in cap_signals:
            self.view.signal_panel.add_signal_card(
                "Git 1,000줄 초과 (Capping)", 
                f"작성자: {sig['author']}\n"
                f"커밋: {sig['hash']}\n"
                f"일자: {sig['date']}\n"
                f"라인수: {sig['additions']} → 1000")
            
        for fs in freq_signals:
            self.view.signal_panel.add_signal_card(
                "빈도 폭주 신호", 
                f"팀원 {fs}의 일일 커밋 수가 평균의 3배를 초과했습니다.")
            
        weights = {
            "git": self.view.slider_git.value() / 100.0,
            "doc": self.view.slider_doc.value() / 100.0,
            "msg": self.view.slider_msg.value() / 100.0
        }
        
        aggregator = ContributionAggregator(mapping)
        self.last_result = aggregator.aggregate(
            capped_git, doc_data, msg_data, weights, self.stopword_dict)
        
        # Z-Score 하위 이상치
        z_signals = ZScoreAnomalyDetector.detect(
            {k: v for k, v in self.last_result["scores"].items()})
        for zs in z_signals:
            self.view.signal_panel.add_signal_card(
                "하위 이상치 (Z-Score)", 
                f"팀원 {zs}의 기여도가 2개 지표 이상에서 매우 낮습니다.")
            
        # FR-5.3: 결측 데이터 경고 배너
        missing_sources = self.last_result.get("missing_sources", [])
        warning_msgs = []
        for src in missing_sources:
            warning_msgs.append(
                f"⚠ {src} 데이터의 형식 불일치 또는 부재로 인해 "
                f"해당 지표가 분석에서 제외되었습니다.")
        self.view.show_warning_banner(warning_msgs)
            
        self.view.charts_view.render_charts(
            self.last_result["scores"], z_signals, missing_sources)
        self.view.btn_export.setEnabled(True)
        
        self._save_cache(self.last_result)
        
    def _export_report(self):
        """FR-5.2: 리포트 저장 (.md / .csv)"""
        if not hasattr(self, 'last_result'): return
        path, _ = QFileDialog.getSaveFileName(
            self.view, "리포트 저장", "", "Markdown (*.md);;CSV (*.csv)")
        if not path: return
        
        scores = self.last_result["scores"]
        missing_sources = self.last_result.get("missing_sources", [])
        
        try:
            if path.endswith(".csv"):
                with open(path, "w", encoding="utf-8-sig") as f:
                    f.write("author,git_score,doc_score,msg_score,total_score\n")
                    for author, data in scores.items():
                        f.write(f"{author},{data['git']},{data['doc']},"
                                f"{data['msg']},{data['total']}\n")
                    for src in missing_sources:
                        f.write(f"\nWARNING,{src} 데이터의 형식 불일치 또는 "
                                f"부재로 인해 해당 지표가 분석에서 제외되었습니다.\n")
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("# QCE 분석 리포트\n\n")
                    f.write("| 이름 | Git점수 | 문서점수 | 메신저점수 | 종합 지표 |\n")
                    f.write("|---|---|---|---|---|\n")
                    for author, data in scores.items():
                        f.write(f"| {author} | {data['git']} | {data['doc']} "
                                f"| {data['msg']} | {data['total']} |\n")
                    for src in missing_sources:
                        f.write(f"\n> ⚠ **경고:** {src} 데이터의 형식 불일치 또는 "
                                f"부재로 인해 해당 지표가 분석에서 제외되었습니다.\n")
                        
            self.view.status_bar.showMessage(
                f"리포트가 성공적으로 저장되었습니다: {path}", 3000)
        except Exception as e:
            QMessageBox.critical(
                self.view, "오류", f"저장 중 오류 발생:\n{str(e)}")
        
    def _save_cache(self, data):
        """NFR-2.3: 원자적 캐시 저장"""
        tmp_path = self.cache_file + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.cache_file)
        except Exception:
            pass
        
    def _load_cache(self):
        """NFR-2.4: 캐시 단독 로드"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.last_result = data
                missing = data.get("missing_sources", [])
                ts = data.get("analysis_timestamp", "알 수 없음")
                
                z_signals = ZScoreAnomalyDetector.detect(
                    {k: v for k, v in data["scores"].items()})
                self.view.charts_view.render_charts(
                    data["scores"], z_signals, missing)
                self.view.btn_export.setEnabled(True)
                self.view.status_bar.showMessage(
                    f"캐시 파일에서 이전 분석 결과를 불러왔습니다. "
                    f"(분석 일시: {ts})", 5000)
            except Exception:
                try:
                    os.remove(self.cache_file)
                except Exception:
                    pass
                QMessageBox.warning(
                    self.view, "오류", 
                    "캐시 파일이 손상되어 삭제되었습니다. 재분석이 필요합니다.")
