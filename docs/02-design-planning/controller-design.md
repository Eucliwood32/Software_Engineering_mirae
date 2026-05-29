# Controller Design (모델-뷰 중재 로직 설계)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-05-29 |
| 상위 문서 | Architecture Overview v1.1, Requirements Record v1.3 |
| 관련 모듈 | `AppController`, `AnalysisOrchestrator` |
| 작성 주체 | QCE 개발팀 (김휘중) |

---

## 1. 개요

본 문서는 QCE 시스템의 **Controller 레이어**에 대한 상세 설계를 기술한다. Controller는 View(사용자 인터페이스)와 Model(비즈니스 로직 및 파싱) 사이의 중재자 역할을 수행하며, 엄격한 MVC 아키텍처(C-4)를 보장하기 위해 설계되었다. 주 역할은 이벤트 라우팅, 비동기 분석 파이프라인의 오케스트레이션, 스레드 수명 관리 등이다.

### 1.1 설계 원칙
- **단방향 의존성 (Strict MVC):** View는 Controller에 사용자 이벤트를 전달하고, Controller는 Model을 호출하여 결과를 받아 다시 View로 Signal을 통해 전달한다. (C-4)
- **UI 응답성 보장:** 무거운 분석 로직은 모두 별도의 Worker Thread에서 실행되어 메인 스레드를 블로킹하지 않아야 한다. (NFR-1.1)
- **모듈 격리 및 통합:** 데이터 소스(Git, 문서, 메신저)의 파서 모듈 중 일부가 실패하더라도 전체 프로세스가 중단되지 않고 가용한 모듈만으로 집계를 수행할 수 있도록 Controller가 오케스트레이션 한다. (NFR-3.2)

---

## 2. 컴포넌트 상세

Controller 레이어는 크게 전역 상태와 라우팅을 담당하는 `AppController`와 백그라운드 분석 작업을 조율하는 `AnalysisOrchestrator`로 분리된다.

### 2.1 AppController

`AppController`는 애플리케이션의 진입점(Entry Point)과 각 View 위젯 간의 이벤트를 라우팅하는 최상위 컨트롤러이다.

- **책임:**
  - `MainWindow` 및 하위 Dialog 초기화 및 의존성 주입.
  - View에서 발생한 사용자 입력(분석 시작, 파일 저장 등)을 캡처하여 적절한 로직 혹은 `AnalysisOrchestrator`로 위임.
  - Worker Thread 작업 완료 시, `AnalysisOrchestrator`로부터 전달받은 결과를 UI 구성요소(`DashboardView` 등)로 전달하여 화면 갱신 (메인 스레드에서 실행).
- **인터페이스 (Python 시그니처):**
  ```python
  class AppController:
      def __init__(self, main_window: 'MainWindow', orchestrator: 'AnalysisOrchestrator'): ...
      
      def route_event(self, event: str, payload: dict) -> None:
          """View에서 발생한 이벤트를 식별하여 라우팅"""
          
      def on_analysis_completed(self, scores: list['MemberScore']) -> None:
          """완료 Signal 수신 후 DashboardView 갱신 지시"""
  ```

### 2.2 AnalysisOrchestrator

`AnalysisOrchestrator`는 비동기 분석 작업의 상태 관리와 Model 레이어 통합을 전담하는 QObject 기반 컴포넌트이다. 

- **책임:**
  - **중복 실행 방지:** `is_analyzing` 플래그를 두어, 진행 중일 때 들어오는 추가 분석 요청을 무시 (NFR-1.2).
  - **Worker 수명 주기 관리:** 분석 시작 시 Worker Thread를 기동하고, 진행률 및 결과를 Signal로 받아 메인 스레드로 안전하게 넘긴다.
  - **모듈 통합:** `DocumentParser`, `GitAnalyzer`, `MessengerParser`를 호출하고, 가용한 결과만을 모아 `ContributionAggregator`로 전달.
- **인터페이스 (Python 시그니처):**
  ```python
  from PyQt6.QtCore import QObject, pyqtSignal

  class AnalysisOrchestrator(QObject):
      progress = pyqtSignal(int)          # 0~100 진행률 (NFR-1.1)
      completed = pyqtSignal(list)        # list[MemberScore] 완료 결과
      failed = pyqtSignal(str)            # 오류 메시지 반환

      is_analyzing: bool = False

      def start_analysis(self, config: dict) -> None:
          """is_analyzing 검사 후 Worker Thread 기동"""
      
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
- 시작 버튼 클릭 시 메인 스레드에서 플래그 검사를 진행하므로, Race Condition이 발생하지 않는다. (NFR-1.2)

---

## 4. 데이터 통합 파이프라인 제어 (NFR-3.2, FR-4.3)

`AnalysisOrchestrator` 내의 Worker Thread는 다음 순서로 Model 컴포넌트들을 제어한다.

1. **데이터 수집 시도:** `DocumentParser`, `GitAnalyzer`, `MessengerParser` 비동기 혹은 순차 호출.
2. **결측 및 에러 방어:** 파서 내부에서 에러가 발생하거나 파일이 없으면 예외를 상위로 전파하지 않고 `None` 혹은 빈 데이터를 반환하도록 한다. (NFR-3.2 격리 원칙).
3. **식별자 통합:** 추출된 작성자 데이터를 `AliasMapper`로 전달하여 N:1 병합 (FR-1.3).
4. **집계 및 스케일링:** `ContributionAggregator`를 호출하여 Capping, Min-Max 정규화, `WeightRebalancer`를 통한 가중치 재조정 수행.
5. **캐싱 및 반환:** 최종 결과 도출 시 `CacheManager.save()` 호출 후 `completed` Signal을 통해 `AppController`로 `MemberScore` 목록 반환 (NFR-2.3).

---

## 5. 아키텍처 RTM 대응 (Controller 부문)

- **C-4 (엄격한 MVC):** `AppController`가 View와 Model을 완전히 격리한다. `AppController`만이 의존성을 조립하고 이벤트를 라우팅한다.
- **NFR-1.1 (비동기 분석):** `AnalysisOrchestrator`와 PyQt Signal-Slot 메커니즘을 통한 워커 스레드 구현.
- **NFR-1.2 (중복 실행 방지):** `is_analyzing` 상태 플래그를 통한 가드(Guard) 처리.
- **NFR-3.2 (모듈 격리):** Worker 내에서 개별 파서를 독립적으로 호출하며, 한 파서의 실패가 다른 파서에 영향을 주지 않고 가용 데이터만 `ContributionAggregator`에 주입되도록 보장한다.
