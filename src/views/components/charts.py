import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


class ChartsView(QWidget):
    """
    FR-5.1: 차트 표시 — 막대(FR-5.1a), 레이더(FR-5.1b), 산점도(FR-5.1c)
    각 차트는 독립 위젯 클래스로 분리 구현된다.
    """
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self._layout.addWidget(self.tabs)
        
        # FR-5.1a 막대 차트
        self.bar_fig = Figure(figsize=(6, 4))
        self.bar_canvas = FigureCanvasQTAgg(self.bar_fig)
        self.tabs.addTab(self.bar_canvas, "종합 기여도")
        
        # FR-5.1b 레이더 차트
        self.radar_fig = Figure(figsize=(6, 4))
        self.radar_canvas = FigureCanvasQTAgg(self.radar_fig)
        self.tabs.addTab(self.radar_canvas, "지표별 레이더 차트")
        
        # FR-5.1c 산점도
        self.scatter_fig = Figure(figsize=(6, 4))
        self.scatter_canvas = FigureCanvasQTAgg(self.scatter_fig)
        self.tabs.addTab(self.scatter_canvas, "Git-문서 산점도")
        
        self.update_empty_state()
        
    def update_empty_state(self):
        """FR-5.1: 분석 미실행 상태 안내 문구"""
        self._clear_figures()
        for fig, canvas in [(self.bar_fig, self.bar_canvas), 
                            (self.radar_fig, self.radar_canvas),
                            (self.scatter_fig, self.scatter_canvas)]:
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "분석을 실행하면 결과가 표시됩니다.", 
                    ha='center', va='center', fontsize=12, color='gray')
            ax.axis('off')
            canvas.draw()
        
    def _clear_figures(self):
        self.bar_fig.clear()
        self.radar_fig.clear()
        self.scatter_fig.clear()
        
    def render_charts(self, results: dict, z_score_signals: list, 
                      missing_sources: list = None):
        """
        results: { "팀원이름": {"git": float, "doc": float, "msg": float, "total": float, ...} }
        z_score_signals: Z-Score 하위 이상치 팀원 이름 리스트
        missing_sources: 결측된 소스 이름 리스트 (예: ["메신저"])
        """
        self._clear_figures()
        if not results:
            self.update_empty_state()
            return
        if missing_sources is None:
            missing_sources = []
            
        team = list(results.keys())
        totals = [results[m]["total"] for m in team]
        gits = [results[m]["git"] for m in team]
        docs = [results[m]["doc"] for m in team]
        msgs = [results[m]["msg"] for m in team]
        
        self._render_bar(team, totals)
        self._render_radar(team, results, missing_sources)
        self._render_scatter(team, gits, docs, msgs, z_score_signals, missing_sources)
        
    # ── FR-5.1a 막대 차트 ──────────────────────────────────────
    def _render_bar(self, team, totals):
        ax = self.bar_fig.add_subplot(111)
        
        # 1위 강조색
        max_idx = totals.index(max(totals)) if totals else -1
        colors = ['#4FC3F7' if i != max_idx else '#FF7043' for i in range(len(team))]
        
        bars = ax.bar(team, totals, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0, 1.2, 0.2))
        ax.set_ylabel("종합 기여 지표")
        ax.set_title("팀원별 종합 기여도")
        ax.grid(axis='y', alpha=0.3)
        
        # 막대 상단 수치 레이블
        for bar, val in zip(bars, totals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{val:.2f}", ha='center', va='bottom', fontsize=9)
        
        # 팀 평균선
        if totals:
            avg = sum(totals) / len(totals)
            ax.axhline(avg, color='gray', linestyle='--', linewidth=1, alpha=0.7)
            ax.text(len(team) - 0.5, avg + 0.02, f"팀 평균: {avg:.2f}", 
                    ha='right', fontsize=8, color='gray')
        
        self.bar_fig.tight_layout()
        self.bar_canvas.draw()
        
    # ── FR-5.1b 레이더 차트 ────────────────────────────────────
    def _render_radar(self, team, results, missing_sources):
        categories = ['Git', '문서', '메신저']
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        ax = self.radar_fig.add_subplot(111, polar=True)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        
        # 결측 소스 표시 — FR-5.1b / FR-5.3
        xlabels = []
        for cat in categories:
            if cat in missing_sources or (cat == "Git" and "Git" in missing_sources) \
               or (cat == "문서" and "문서" in missing_sources) \
               or (cat == "메신저" and "메신저" in missing_sources):
                xlabels.append(f"{cat}\n(제외됨)")
            else:
                xlabels.append(cat)
        ax.set_xticklabels(xlabels)
        ax.set_ylim(0, 1.0)
        ax.set_yticks(np.arange(0.2, 1.2, 0.2))
        
        # 팀원별 폴리곤
        cmap = plt.cm.Set2
        for i, m in enumerate(team):
            values = [results[m]["git"], results[m]["doc"], results[m]["msg"]]
            values += values[:1]
            color = cmap(i % 8)
            ax.plot(angles, values, linewidth=1.5, linestyle='solid', label=m, color=color)
            ax.fill(angles, values, alpha=0.08, color=color)
        
        # 팀 평균 폴리곤 오버레이 — FR-5.1b
        if team:
            avg_git = sum(results[m]["git"] for m in team) / len(team)
            avg_doc = sum(results[m]["doc"] for m in team) / len(team)
            avg_msg = sum(results[m]["msg"] for m in team) / len(team)
            avg_vals = [avg_git, avg_doc, avg_msg, avg_git]
            ax.plot(angles, avg_vals, linewidth=1.5, linestyle='--', 
                    label="팀 평균", color='gray')
            
        ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=8)
        self.radar_fig.tight_layout()
        self.radar_canvas.draw()
        
    # ── FR-5.1c 산점도 ─────────────────────────────────────────
    def _render_scatter(self, team, gits, docs, msgs, z_signals, missing_sources):
        ax = self.scatter_fig.add_subplot(111)
        
        # FR-5.1c: X=Git 점수, Y=문서 점수, 크기=메신저
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        
        # 사분면 배경색 — FR-5.1c
        ax.axvspan(0.5, 1.05, ymin=0.5/1.1 + 0.045, ymax=1.0, 
                   color='#C8E6C9', alpha=0.3)  # 올라운더 (연초록)
        ax.axvspan(0.5, 1.05, ymin=0.0, ymax=0.5/1.1 + 0.045, 
                   color='#BBDEFB', alpha=0.3)  # 개발 집중 (연파랑)
        ax.axvspan(-0.05, 0.5, ymin=0.5/1.1 + 0.045, ymax=1.0, 
                   color='#FFE0B2', alpha=0.3)  # 문서 집중 (연주황)
        ax.axvspan(-0.05, 0.5, ymin=0.0, ymax=0.5/1.1 + 0.045, 
                   color='#E0E0E0', alpha=0.3)  # 저참여 (연회색)
        
        # 사분면 레이블
        ax.text(0.95, 0.95, "올라운더", ha='right', va='top', fontsize=8, color='green', alpha=0.7)
        ax.text(0.95, 0.05, "개발 집중", ha='right', va='bottom', fontsize=8, color='blue', alpha=0.7)
        ax.text(0.05, 0.95, "문서 집중", ha='left', va='top', fontsize=8, color='orange', alpha=0.7)
        ax.text(0.05, 0.05, "저참여", ha='left', va='bottom', fontsize=8, color='gray', alpha=0.7)
        
        msg_missing = "메신저" in missing_sources
        
        # 점 크기: 메신저 점수 비례 (40~200pt) — FR-5.1c
        if msg_missing:
            sizes = [80] * len(team)  # 메신저 결측 시 80pt 고정
        else:
            sizes = [40 + (m * 160) for m in msgs]  # 40pt(0.0) ~ 200pt(1.0)
        
        for i, m in enumerate(team):
            color = 'red' if m in z_signals else '#1976D2'
            marker = 'o'
            
            if msg_missing:
                ax.scatter(gits[i], docs[i], s=sizes[i], color=color, alpha=0.7,
                          edgecolors='gray', linewidths=1.5, linestyle='--', zorder=3)
            else:
                ax.scatter(gits[i], docs[i], s=sizes[i], color=color, alpha=0.7,
                          edgecolors='white', linewidths=0.5, zorder=3)
            
            # Z-Score 하위 이상치 강조 — FR-4.2d, FR-5.1c
            if m in z_signals:
                ax.annotate("⚠", (gits[i], docs[i]), fontsize=14, ha='center', 
                           va='center', color='red', zorder=4)
            
            # 팀원명 라벨
            ax.annotate(m, (gits[i] + 0.02, docs[i] + 0.02), fontsize=8, zorder=5)
        
        # 팀 평균 십자선 — FR-5.1c
        if gits:
            avg_x = np.mean(gits)
            avg_y = np.mean(docs)
            ax.axvline(avg_x, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            ax.axhline(avg_y, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            ax.plot(avg_x, avg_y, marker='+', color='gray', markersize=12, 
                    markeredgewidth=2, zorder=4)
            ax.annotate("팀 평균", (avg_x + 0.03, avg_y + 0.03), 
                        fontsize=7, color='gray')
        
        ax.set_xlabel("Git 점수")
        ax.set_ylabel("문서 점수")
        ax.set_title("Git-문서 산점도 (크기: 메신저)")
        ax.grid(alpha=0.2)
        
        self.scatter_fig.tight_layout()
        self.scatter_canvas.draw()
