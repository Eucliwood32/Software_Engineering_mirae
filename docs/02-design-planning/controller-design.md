# Controller Design (모델-뷰 중재 로직 설계)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.5 |
| 작성일 | 2026-06-01 |
| 상위 문서 | Architecture Overview v1.3, Requirements Record v1.5, View Design v1.4 |
| 관련 모듈 | `AppController`, `AnalysisOrchestrator` |
| 작성 주체 | QCE 개발팀 (김휘중) |

---

## 1. 개요

본 문서는 QCE 시스템의 **Controller 레이어**에 대한 상세 설계를 기술한다. Controller는 View(사용자 인터페이스)와 Model(비즈니스 로직 및 파싱) 사이의 중재자 역할을 수행하며, 엄격한 MVC 아키텍처(C-4)를 보장하기 위해 설계되었다. 주 역할은 이벤트 라우팅, 3-스크린 전환 조율, 비동기 분석 파이프라인의 오케스트레이션, 스레드 수명 관리, 결과 화면 계정 병합 재집계 등이다.

### 1.1 설계 원칙
- **단방향 의존성 (Strict MVC):** View는 Controller에 사용자 이벤트를 전달하고, Controller는 Model을 호출하여 결과를 받아 다시 View로 Signal을 통해 전달한다. (C-4)
- **UI 응답성 보장:** 무거운 분석 로직은 모두 별도의 Worker Thread에서 실행되어 메인 스레드를 블로킹하지 않아야 한다. (NFR-1.1)
- **모듈 격리 및 통합:** 데이터 소스(Git, 문서, 메신저)의 파서 모듈 중 일부가 실패하더라도 전체 프로세스가 중단되지 않고 가용한 모듈만으로 집계를 수행할 수 있도록 Controller가 오케스트레이션한다. (NFR-3.2)
- **View 타입 격리 (INV-V1):** Controller가 `MemberScore`를 View로 전달하기 직전 `dataclasses.asdict()`로 plain dict로 직렬화한다. View는 `MemberScore` 타입을 import하지 않는다.

---

## 2. 컴포넌트 상세

Controller 레이어는 크게 전역 상태와 라우팅을 담당하는 `AppController`와 백그라운드 분석 작업을 조율하는 `AnalysisOrchestrator`로 분리된다.

### 2.1 AppController

`AppController`는 애플리케이션의 진입점(Entry Point)과 3-스크린 전환, 각 View 위젯 간의 이벤트를 라우팅하는 최상위 컨트롤러이다.

- **책임:**
  - `MainWindow`(`QStackedWidget` 셸) 및 3-스크린(`SubmitScreen`, `LoadingScreen`, `ResultScreen`) 초기화 및 의존성 주입.
  - **화면 전환 조율 (FR-5.4):** 생명주기별 `MainWindow.show_submit()/show_loading()/show_result()` 호출.
  - View에서 발생한 사용자 입력(분석 시작, 병합 요청 등)을 캡처하여 적절한 로직 혹은 `AnalysisOrchestrator`로 위임.
  - Worker Thread 작업 완료 시, `AnalysisOrchestrator`로부터 전달받은 `MemberScore` 목록을 `dataclasses.asdict()`로 직렬화 후 `ResultScreen.render(score_dicts, missing)` 호출 (INV-V1).
  - 결과 화면 병합 요청(`merge_requested`) 수신 시 원시 지표 재집계 흐름 조율 (FR-5.7).
  - `on_new_analysis_requested()`: 
    - Tracker 캐시 비우기
    - **Controller 내부 입력 경로 캐시**(`_doc_paths`, `_git_path`, `_msg_path`) 비우기
    - **Orchestrator의 이전 분석 데이터**(`reset()`) 비우기
    - SubmitScreen 파일 목록 UI 비우기
    - 결과적으로 상태를 프로그램 초기 기동 상태로 완전 리셋한 뒤 `show_submit()` 호출.

- **화면 전환 생명주기 (FR-5.4):**

  | 조건 | 전환 |
  | :--- | :--- |
  | 기동 — 캐시 없음 | `show_submit()` |
  | 기동 — 캐시 단독 로드 성공 | 즉시 `show_result()` (NFR-2.4) |
  | `analyze_clicked` (가중치 합 100%) | `show_loading()` |
  | `completed` | `show_result()` |
  | `failed` | `show_submit()` + 오류 안내 |
  | `new_analysis_requested` | 상태 초기화 → `show_submit()` |
  | `merge_requested` | `show_loading()` → 재집계 완료 → `show_result()` |

- **인터페이스 (Python 시그니처):**
  ```python
  import dataclasses
  
  class AppController:
      def __init__(self, main_window: 'MainWindow', orchestrator: 'AnalysisOrchestrator'): ...
  
      # --- 화면 전환 조율 ---
      def _connect_signals(self) -> None:
          """View 신호와 슬롯을 연결. 추가 신호 목록은 §2.1 (b) 참조."""
  
      # --- 분석 흐름 ---
      def on_analyze_clicked(self, config: dict) -> None:
          """SubmitScreen.analyze_clicked 수신 → show_loading() → start_analysis()"""
  
      def on_analysis_completed(self, scores: list['MemberScore']) -> None:
          """completed Signal 수신 → asdict 직렬화 → ResultScreen.render → show_result()"""
          score_dicts = [dataclasses.asdict(s) for s in scores]
          # self.main_window.result_screen.render(score_dicts, missing)
          # self.main_window.show_result()
  
      def on_analysis_failed(self, message: str) -> None:
          """failed Signal 수신 → show_submit() + 오류 안내"""
  
      # --- 신규: 병합 재집계 ---
      def on_merge_requested(self, mapping: dict) -> None:
          """ResultScreen.merge_requested 수신 → show_loading() → 재집계 (FR-5.7, §6 참조)"""
  
      def on_new_analysis_requested(self) -> None:
        """ResultScreen.new_analysis_requested 수신 → 이전 적재 파일명/저장소 등 상태 완전 초기화(리셋) 명령 하달 → show_submit()"""

      # --- 신규: 신호 예외 처리 (FR-4.2c) ---
      def on_signal_dismissed(self, author: str, signal_type: str, ref: str) -> None:
          """ResultScreen.signal_dismissed 수신 → NormalizedSignalsTracker.dismiss()
             → _render_results()로 재렌더(재집계 없음, 점수 불변, STR-7)."""

      def _render_results(self) -> None:
          """신호 예외(tracker) 반영 렌더: tracker.apply(_last_scores) → asdict 직렬화
             → ResultScreen.render → set_suggested_mapping(AliasExtractor 추천)."""
  ```

  > **신호 예외·신원 추천 배선 (c).** Controller는 `NormalizedSignalsTracker`(FR-4.2c)와 `AliasExtractor`(FR-1.3)를 보유하고, 원본 `scores`를 `_last_scores`로 보관한다. (1) 신호 카드 "정상으로 표시"는 `ResultScreen.signal_dismissed(author,type,ref)`로 올라와 `tracker.dismiss()` 후 `_render_results()`로 *재집계 없이* 표시만 갱신한다(점수 불변, STR-7). 새 분석 시 `tracker.clear()`. (2) `_render_results()`는 결과 인물에 `AliasExtractor.suggest_groups`로 병합 후보(대표명≠원본 군집)를 만들어 `ResultScreen.set_suggested_mapping`으로 전달한다(자동 병합 아님, 조장 확정). Model 호출은 Controller가, View엔 dict만 전달 → C-4·INV-V1 준수.

- **신호 connect 대상 (b):**
  - **추가:** `SubmitScreen.documents_dropped`, `SubmitScreen.git_repo_chosen`, `SubmitScreen.messenger_dropped`, `SubmitScreen.analyze_clicked`(또는 SubmitScreen 중계), `ResultScreen.merge_requested(dict)`, `ResultScreen.new_analysis_requested()`, `ResultScreen.signal_dismissed(str,str,str)` (FR-4.2c)
  - **제거:** `alias_mapping_requested` — 분석-전 매핑 모달 신호 폐기 (FR-1.3 일원화)
  - 입력 드롭 신호 발신 주체: ~~MainWindow~~ → **SubmitScreen**

### 2.2 AnalysisOrchestrator

`AnalysisOrchestrator`는 비동기 분석 작업의 상태 관리와 Model 레이어 통합을 전담하는 QObject 기반 컴포넌트이다.

- **책임:**
  - **중복 실행 방지:** `is_analyzing` 플래그를 두어, 진행 중일 때 들어오는 추가 분석 요청(병합 재집계 포함)을 무시 (NFR-1.2).
  - **Worker 수명 주기 관리:** 분석 시작 시 Worker Thread를 기동하고, 진행률 및 결과를 Signal로 받아 메인 스레드로 안전하게 넘긴다.
  - **모듈 통합:** `DocumentParser`, `GitAnalyzer`, `MessengerParser`를 호출하고, 가용한 결과만을 모아 `ContributionAggregator`로 전달.
  - **원시 지표 보유:** 1차 분석에서 수집한 원시 지표(커밋/글자수/발화수)를 세션 동안 내부 상태로 보유하여, 병합 재집계 시 파서를 재실행하지 않고 원시 지표 + 새 매핑으로 재집계 가능하게 한다 (FR-5.7).
  
- **인터페이스 (Python 시그니처):**
  ```python
  from PyQt6.QtCore import QObject, pyqtSignal

  class AnalysisOrchestrator(QObject):
      progress  = pyqtSignal(int)   # 0~100 진행률 (NFR-1.1)
      completed = pyqtSignal(list)  # list[MemberScore] 완료 결과
      failed    = pyqtSignal(str)   # 오류 메시지 반환

      is_analyzing: bool = False

      # 원시 지표 보유 (병합 재집계용)
      _raw_git:  dict | None = None   # {alias: CommitStats}
      _raw_docs: dict | None = None   # {alias: int}
      _raw_msgs: dict | None = None   # {alias: int}

      def start_analysis(self, config: dict) -> None:
          """is_analyzing 검사 후 Worker Thread 기동. 1차 분석은 항등 매핑(§4 3단계)."""

      def start_merge_reaggregation(self, mapping: dict) -> None:
          """병합 매핑 수신 → is_analyzing 가드 → 원시 지표 + mapping으로 재집계 (§6)."""

      def _on_worker_finished(self) -> None:
          """종료 시 (성공, 실패, 취소 무관) is_analyzing=False 및 UI 버튼 재활성 Signal 발행"""
  ```

---

## 3. 동시성 및 스레드 모델

분석 연산 중 UI 프리징을 막기 위해 PyQt의 Thread 모델을 사용한다. (NFR-1.1, C-5)

### 3.1 Worker Thread 구조
1. **QRunnable / QThread:** 실제 분석(파싱, 정규화, 집계) 코드는 `QThread` 혹은 `QRunnable`을 상속받은 Worker 안에서 실행된다.
2. **Signal 경계 불변식:** Worker 스레드는 직접 View의 위젯(ProgressBar 등) 속성을 변경할 수 없다. 오직 `progress`, `completed`, `failed` Signal만 발행하며, 이 Signal에 연결된 메인 스레드의 슬롯(Slot)에서 View를 갱신한다.

### 3.2 중복 및 동시 접근 제어
- `AnalysisOrchestrator`의 `is_analyzing` 상태는 메인 스레드에서만 읽고 쓰인다.
- 시작 버튼 클릭 시, **그리고 병합 재집계 요청 시** 메인 스레드에서 플래그 검사를 진행하므로 Race Condition이 발생하지 않는다. (NFR-1.2)

---

## 4. 데이터 통합 파이프라인 제어 (NFR-3.2, FR-4.3, FR-1.3)

`AnalysisOrchestrator` 내의 Worker Thread는 다음 순서로 Model 컴포넌트들을 제어한다.

1. **데이터 수집 시도:** `DocumentParser`, `GitAnalyzer`, `MessengerParser` 비동기 혹은 순차 호출.
2. **결측 및 에러 방어:** 파서 내부에서 에러가 발생하거나 파일이 없으면 예외를 상위로 전파하지 않고 None 혹은 빈 데이터를 반환하도록 한다. (NFR-3.2 격리 원칙). 각 파서의 원시 결과를 Orchestrator 내부에 보유하며, **특히 카카오톡 등 단일 데이터 소스만 입력된 경우에도 파이프라인이 붕괴하지 않고 정상적으로 집계 단계로 넘어가도록 철저히 보장한다.**
3. **식별자 통합 (FR-1.3 개정):**
   - **1차 분석:** `AliasMapper`에 **항등 매핑**을 전달하여 각 식별자를 독립 인물로 산출한다. 분석-전 매핑 모달(alias_mapping_requested)은 폐기되었다.
   - **병합 재집계(FR-5.7):** 결과 화면에서 조장이 병합 매핑을 제출하면 파서를 재실행하지 않고, 보유 중인 원시 지표에 새 매핑을 적용해 `AliasMapper.merge(raw, mapping)` → `ContributionAggregator.aggregate(...)` 경로를 재실행한다. (§6 참조)
4. **집계 및 스케일링:** `ContributionAggregator`를 호출하여 Capping, Max 정규화, `WeightRebalancer`를 통한 가중치 재조정 수행. (1차 분석과 병합 재집계 모두 동일 경로)
5. **캐싱 및 반환:** 최종 결과 도출 시 `CacheManager.save()` 호출 후 `completed` Signal을 통해 `AppController`로 `MemberScore` 목록 반환 (NFR-2.3). `AppController`가 `dataclasses.asdict()`로 직렬화 후 `ResultScreen.render`에 전달 (INV-V1).

---

## 5. 아키텍처 RTM 대응 (Controller 부문)

| 요구사항 | 대응 설계 |
| :--- | :--- |
| C-4 (엄격한 MVC) | `AppController`가 View와 Model을 완전히 격리. `AppController`만이 의존성을 조립하고 이벤트를 라우팅 |
| NFR-1.1 (비동기 분석) | `AnalysisOrchestrator`와 PyQt Signal-Slot 메커니즘을 통한 워커 스레드 구현 |
| NFR-1.2 (중복 실행 방지) | `is_analyzing` 상태 플래그를 통한 가드(Guard) 처리. 병합 재집계 중 추가 요청도 차단 |
| NFR-2.4 (캐시 단독 로드) | 기동 시 캐시 존재 시 `show_result()` 즉시 전환 |
| NFR-3.2 (모듈 격리) | Worker 내에서 개별 파서를 독립적으로 호출하며, 한 파서의 실패가 다른 파서에 영향을 주지 않고 가용 데이터만 `ContributionAggregator`에 주입 |
| FR-1.3 (신원 매핑, 개정) | 1차 분석은 항등 매핑으로 통과. 병합은 결과 화면 사후 재집계 경로로 처리. 병합 후보는 `AliasExtractor.suggest_groups`로 추천(결정론, 자동병합 아님) → `set_suggested_mapping` |
| FR-4.2c (신호 예외 처리) | `on_signal_dismissed` → `NormalizedSignalsTracker.dismiss()` → `_render_results()` 재렌더(재집계 없음, 점수 불변). 새 분석 시 `tracker.clear()` |
| FR-5.4 (3-스크린 전환) | `AppController`가 생명주기별 `show_submit()/show_loading()/show_result()` 호출 |
| FR-5.7 (결과 화면 계정 병합) | `on_merge_requested` → `start_merge_reaggregation` → 원시 지표 재집계 → 재렌더 |
| INV-V1 (View 타입 격리) | `on_analysis_completed`/`_render_results`에서 `dataclasses.asdict()` 직렬화 후 View에 push |

---

## 6. 결과 화면 계정 병합 재집계 흐름 (FR-5.7) [신규]

조장이 `ResultScreen`에서 동일인의 여러 계정을 1인으로 병합하면, Controller가 다음 순서로 재집계를 조율한다.

```
ResultScreen.merge_requested(mapping={alias → member})
  → AppController.on_merge_requested(mapping)
  → AnalysisOrchestrator.start_merge_reaggregation(mapping)
       └─ is_analyzing 가드 (NFR-1.2): 진행 중이면 즉시 return
       └─ is_analyzing = True → show_loading()
       └─ Worker Thread 기동:
            AliasMapper.merge(raw_git, mapping)     # N:1 합산 (FR-1.3)
            AliasMapper.merge(raw_docs, mapping)
            AliasMapper.merge(raw_msgs, mapping)
            → ContributionAggregator.aggregate(     # Capping→정규화→가중치 재조정
                git=merged_git, docs=merged_docs, msgs=merged_msgs, weights=current_weights)
            → CacheManager.save(...)                # 병합 결과도 캐싱
            → completed.emit(scores)
  → AppController.on_analysis_completed(scores)
       └─ dataclasses.asdict() 직렬화
       └─ ResultScreen.render(score_dicts, missing)
       └─ show_result()
```

### 설계 불변식
- **재정규화 필수 (FR-4.1):** 병합으로 팀원 집합이 바뀌면 Max 정규화 기준이 달라진다. 시각적 점수 합산이 아니라 `ContributionAggregator.aggregate` 재실행이 필요하다.
- **원시 지표 보존:** Orchestrator는 1차 분석에서 수집한 `{alias: CommitStats}`, `{alias: chars}`, `{alias: messages}` 원시 지표를 세션 내내 보유한다. 병합은 파서를 다시 실행하지 않는다.
- **결정론 (NFR-1.3):** 동일 병합 매핑 + 동일 원시 지표 = 동일 결과.
- **분리(병합 취소):** 매핑을 갱신하여 동일 재집계 경로로 처리.
- **중복 가드 (NFR-1.2):** 재집계 중 추가 병합 요청은 `is_analyzing` 플래그로 차단.

---

## 7. 문서 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-05-29 | 최초 작성. `AppController`/`AnalysisOrchestrator` 기본 설계. | QCE 개발팀 |
| **v1.1** | **2026-05-31** | **(1) 3-스크린 전환 조율 추가 (FR-5.4). (2) 분석-전 매핑 모달 폐기·1차 분석 항등 매핑으로 FR-1.3 개정 반영. (3) 결과 화면 계정 병합 재집계 흐름 신규 §6 추가 (FR-5.7). (4) View 타입 격리(INV-V1) — asdict 직렬화 명시. (5) AnalysisOrchestrator에 원시 지표 보유 책임 추가. (6) AppController 신호 connect 목록 갱신 (merge_requested, new_analysis_requested 추가, alias_mapping_requested 제거). (7) RTM §5 갱신 (FR-5.4, FR-5.7, NFR-2.4, INV-V1, FR-1.3 개정). (8) 상위 문서를 Architecture v1.2·RR v1.4·View Design v1.3로 갱신.** | QCE 개발팀 |
| **v1.2** | **2026-05-31** | **구 SRS.md 폐지 반영 — 신호 예외 처리·신원 추천 배선 추가. (1) §2.1 인터페이스에 `on_signal_dismissed`·`_render_results` 추가 및 배선 설명(c) — `NormalizedSignalsTracker`(FR-4.2c) 보유, "정상으로 표시"는 재집계 없이 표시만 갱신(점수 불변, STR-7), 새 분석 시 `tracker.clear()`. (2) `_render_results`가 `AliasExtractor.suggest_groups`로 병합 후보를 만들어 `set_suggested_mapping`으로 전달(FR-1.3, 자동병합 아님). (3) 신호 connect 목록에 `ResultScreen.signal_dismissed` 추가. (4) RTM §5에 FR-4.2c 행 추가, FR-1.3 행에 추천 명시. (5) 상위 문서를 Architecture v1.3·RR v1.5·View Design v1.4로 갱신.** | QCE 개발팀 |
| v1.3 | 2026-06-01 | 사용자 피드백(UX 버그 개선) 반영: (1) §2.1 AppController의 on_new_analysis_requested 시그니처에 [새 분석] 진입 시 파일명/저장소 등 이전 뷰 데이터의 완전 초기화(리셋) 제어 책임 명문화. (2) §4 파이프라인 제어 원칙에 카카오톡 등 단일 소스 입력 시의 파이프라인 정상 구동 보장 명시. | QCE 개발팀 |
| **v1.4** | **2026-06-01** | **사용자 피드백(슬라이더 비례 분배·표기 개선) 반영: (1) §2.1 화면 전환 조건표에서 가중치 합 표기를 1.0에서 100%로 변경. (2) `_on_weights_changed` 경고 문구를 퍼센트 단위로 변경.** | QCE 개발팀 |
| **v1.5** | **2026-06-01** | **버그 수정(새 분석 시 이전 데이터 잔존) 반영: §2.1 `on_new_analysis_requested` 시그니처에 Controller 내부 입력 캐시(`_doc_paths` 등) 및 Orchestrator 데이터 초기화 책임 명시.** | QCE 개발팀 |
| **v1.6** | **2026-06-02** | **전역 문서 업데이트의 일환 (Capping 한도 상향 및 UI/UX 디자인 개선 변경사항 동기화).** | 이대한, 김휘중 공동 작업 |
