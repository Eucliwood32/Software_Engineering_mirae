# Model Business Logic 설계 (Model BusinessLogic Design)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.6 |
| 작성일 | 2026-06-01 |
| 상위 문서 | Architecture Overview v1.3, Requirements Record v1.5, Development Constraints v2.0, Controller Design v1.2 |
| 관련 ADR | ADR-0004 (JSON 캐시 vs pickle) |
| 작성 주체 | QCE 개발팀 (김휘중) |

---

## 1. 개요

### 1.1 목적
본 문서는 QCE 시스템의 **Model · BusinessLogic 레이어**에 속하는 9개 클래스의 상세 설계를 기술한다. 각 클래스의 책임, 인터페이스 시그니처, 핵심 알고리즘, 그리고 해당 컴포넌트가 실현하는 요구사항과 구속받는 제약사항을 명시한다.

### 1.2 범위
Architecture Overview §5.3에서 정의된 레이어 경계 시그니처 위에서, 내부 알고리즘과 필드 단위 상세를 다룬다. 파서(Parsing) 레이어는 별도 문서(`model-parser-design.md`)에서 다루며, Controller 레이어는 `controller-design.md`에서 다룬다.

### 1.3 설계 불변식
- **PyQt6 import 금지.** Model 레이어의 어떤 모듈도 `PyQt6` 심볼을 import하지 않는다. 이로써 Model은 UI 프레임워크와 독립적으로 pytest 단위 테스트가 가능하다 (Architecture Overview §3.2, NFR-3.2 검증 전제).
- **파서 직접 import 금지.** BusinessLogic 모듈은 Parsing 모듈을 직접 import하지 않는다. 모든 통합은 Controller의 `AnalysisOrchestrator`가 수행한다 (NFR-3.2, C-4).
- **판정 금지 원칙.** 이상 신호(`AnomalySignalDetector`)의 출력은 점수 산출 경로와 분리되어 있으며, 종합 점수에 자동 반영되지 않는다 (STR-7, ConOps P5).
- **결정론 보장.** 동일 입력과 동일 가중치 설정에 대해 종합 기여 지표는 동일하게 산출된다 (NFR-1.3).

### 1.4 참조 데이터 타입
본 문서의 클래스들은 Architecture Overview §5.1에 정의된 공용 데이터 타입을 사용한다.

```python
from dataclasses import dataclass, field

@dataclass
class CommitStats:                      # FR-2.1
    commits: int
    additions: int
    deletions: int
    commits_list: list = field(default_factory=list)
    # commits_list[i] = {"hash", "date", "additions", "deletions"} — 커밋 단위 명세.
    # FR-4.2(커밋별 Capping)·FR-4.2b(빈도 신호)·타임라인 시각화의 근거 데이터.

@dataclass
class MemberScore:                      # FR-4.* 통합 결과
    author: str
    git_score: float                    # 0.0~1.0
    doc_score: float                    # 0.0~1.0
    msg_score: float                    # 0.0~1.0
    total_score: float                  # 0.0~1.0
    raw_additions: int                  # [개선] UI 툴팁 노출용 Git 원시 데이터
    raw_chars: int                      # [개선] UI 툴팁 노출용 문서 유효 글자수
    raw_messages: int                   # [개선] UI 툴팁 노출용 메신저 유효 발화수
    capping_applied: bool
    signals: list[str] = field(default_factory=list)        # 표시 라벨 예: ["CAPPING","EW-02","ZSCORE"]
    signal_details: list[dict] = field(default_factory=list)  # 신호 카드 표시·FR-4.2c 예외용(아래)
    commit_dates: list[str] = field(default_factory=list)     # 커밋 일자(YYYY-MM-DD) 목록
    dimensions: dict[str, float] = field(default_factory=dict) # [v1.7] 레이더 세부 축(가용 소스별 3키, 표시 전용)
```

> **`dimensions` (v1.7, FR-5.1b 레이더 세부 축).** 가용 소스마다 3개의 세부 지표를 Min-Max 정규화(0.0~1.0)한 dict. 결측 소스의 키는 포함하지 않으므로 가용 소스 1·2·3개에 각각 3·6·9개 키가 담긴다. 세부 지표는 다음과 같으며 모두 *표시 전용*(STR-7, `total_score` 비반영)이다.
> - **Git** (`CommitStats`에서 산출): `git_commits`(커밋 수) · `git_additions`(추가 라인, Capping+로그스케일) · `git_deletions`(삭제 라인, 로그스케일)
> - **문서** (`doc_details`에서 산출): `doc_chars`(유효 글자수) · `doc_count`(작성 문서 수) · `doc_blocks`(문단·도형 등 구성 요소 수)
> - **메신저** (`msg_details`에서 산출): `msg_count`(발화 수) · `msg_chars`(발화 글자수) · `msg_hours`(활동 시간대 수)

> **`signal_details` 원소 구조 (FR-4.2/4.2b/4.2d 카드 표시·FR-4.2c 예외 처리용):**
> - CAPPING: `{"type":"CAPPING","hash","date","additions"}`
> - EW-02: `{"type":"EW-02","date","period_commits","baseline_avg"}`
> - ZSCORE: `{"type":"ZSCORE","metrics":[...]}`
>
> `signals`(문자열 라벨)와 병행 유지하여 하위호환을 보장한다. 두 필드 모두 종합 점수에
> 반영되지 않는 *표시 전용* 데이터다(STR-7). View는 `dataclasses.asdict()`로 직렬화된
> 점수 dict의 `signal_details`만 소비한다(INV-V1).

---

## 2. 컴포넌트 상세 설계

### 2.1 Normalizer (FR-4.1)

- **책임:** 이질적 단위의 지표 3종(Git 추가 라인, 문서 유효 글자수, 메신저 유효 발화 수)을 0.0~1.0 척도로 변환(Min-Max 정규화).
- **시그니처:**
  ```python
  class Normalizer:
      def normalize(self, values: list[float]) -> list[float]:
          """(x-min)/(max-min). max==min이면 전원 0.5. round(_, 4)."""
  ```
- **알고리즘:**
  1. 입력 리스트에서 `min`, `max`를 산출한다.
  2. `max == min`인 경우 분산 0으로 간주하여 모든 반환값을 `0.5`로 설정한다 (ZeroDivisionError 방지).
  3. 그 외의 경우 `(x - min) / (max - min)`을 수행한다.
  4. 모든 결과를 소수점 4자리에서 반올림한다 (`round(_, 4)`).
  5. 빈 리스트(`[]`) 입력 시 빈 리스트를 반환하며 예외를 발생시키지 않는다.
- **사후조건:** 모든 반환값 v에 대해 `0.0 ≤ v ≤ 1.0`.

---

### 2.2 CappingScaler (FR-4.2)

- **책임:** 단일 커밋의 비정상적 대량 추가(예: 자동 생성 코드 일괄 커밋, 보일러플레이트 투입)에 의한 지표 왜곡을 방지하기 위해 추가 라인 수를 상한치로 제한하고(Capping), 합산값에 로그 스케일을 적용한다.
- **상수:** `CAPPING_THRESHOLD: int = 1000`
- **시그니처:**
  ```python
  class CappingScaler:
      CAPPING_THRESHOLD: int = 1000
      def cap(self, additions: int) -> tuple[int, bool]:
          """additions > 1000 → (1000, True). 그 외 (additions, False)."""
      def log_scale(self, total: int) -> float:
          """math.log1p(total)."""
  ```
- **알고리즘:**
  - `cap()`: `additions > CAPPING_THRESHOLD`이면 `(1000, True)`, 그렇지 않으면 `(additions, False)`. 경계값 `1000`은 Capping을 발동시키지 않는다 (`>`만 cap).
  - `log_scale()`: `math.log1p(total)`을 반환한다. `total == 0`이면 `0.0`.
- **신호 연동:** Capping이 발생한 커밋은 `ContributionAggregator`를 통해 `MemberScore.capping_applied = True`로 기록되며, 조장에게 신호 목록(작성자·커밋 식별·변경량)으로 표시된다 (ConOps SC-A 8단계, SC-B 1단계).

---

### 2.3 AnomalySignalDetector (FR-4.2, FR-4.2b, FR-4.2c, FR-4.2d)

- **책임:** 통계적·규칙적 이상 징후를 식별하여 조장에게 표시하기 위한 신호를 생성한다. **최종 평가 점수에는 자동 반영되지 않으며** (ConOps P5 판정 금지 원칙, STR-7), 조장의 의사결정을 돕는 보조 지표로만 사용된다. 신호는 혐의 제기가 아니라 **검증 권유**이다 (ConOps §7.2).
- **시그니처:**
  ```python
  class AnomalySignalDetector:
      def detect_frequency(self, repo: dict[str, CommitStats]) -> list[dict]:
          """작성자 단기 커밋 빈도가 평소 일평균의 3배 초과 구간을 신호로.
             반환: [{author, period, period_commits, baseline_avg}, ...]"""
      def detect_capping(self, repo: dict[str, CommitStats]) -> list[dict]:
          """단일 커밋 추가 라인 > 1000인 커밋을 신호로(해시 7자 축약).
             반환: [{author, hash, date, additions}, ...]"""
      def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
          """정규화 지표 Z-Score ≤ -1.5가 2개 이상인 팀원명 리스트."""
      def detect_zscore_detail(self, scores: list[MemberScore]) -> list[dict]:
          """detect_zscore 상세판. 반환: [{author, metrics:[하위 지표명...]}, ...]"""
      def build_signal_details(
          self, repo: dict[str, CommitStats] | None, scores: list[MemberScore]
      ) -> dict[str, list[dict]]:
          """팀원별 구조화 신호 상세 묶음 {author: [detail, ...]} (카드 표시용)."""
  ```
- **알고리즘:**
  - `detect_frequency()` (EW-02, FR-4.2b): 작성자별 일자별 커밋 시계열을 구성하여, 특정 일자의 커밋 수가 해당 작성자의 일평균 커밋 수의 3배를 초과하는 구간을 식별한다. 각 신호 항목은 `author`, `period`, `period_commits`, `baseline_avg`를 포함한다.
  - `detect_capping()` (FR-4.2): `CommitStats.commits_list`를 순회하여 단일 커밋 추가 라인이 1,000을 초과하는 커밋을 신호 항목(작성자·커밋 해시 7자·작성일·변경 라인 수)으로 반환한다. (`commits_list`가 비어 있으면 빈 목록 — GitAnalyzer가 커밋 명세를 채워야 동작하며, `model-parser-design.md` 참조.)
  - `detect_zscore()` / `detect_zscore_detail()` (FR-4.2d): 정규화된 지표(Git, 문서, 메신저)에 대해 팀원별 Z-Score를 산출하고, Z-Score가 -1.5 이하인 항목이 2개 이상 존재하는 팀원을 식별한다. `detect_zscore`는 이름 리스트를, `detect_zscore_detail`은 해당 팀원의 하위 지표명(`metrics`)을 함께 반환한다. 신호 대상 팀원은 산점도(FR-5.1c)에서 붉은색 + ⚠ 오버레이로 강조 표시된다.
  - `build_signal_details()`: 위 탐지 결과를 `MemberScore.signal_details` 스키마(§1.4)로 통합하여 팀원별로 묶는다. CAPPING·EW-02·ZSCORE 세 유형을 단일 구조로 합치며, 신호 카드 패널(`AnomalySignalPanel`, view-design)과 예외 처리(`NormalizedSignalsTracker`, §2.10)의 입력이 된다.
- **격리 원칙:** 이 클래스의 출력은 `MemberScore.signals`/`signal_details`에 기록되지만, `total_score` 계산 경로에는 투입되지 않는다.

---

### 2.4 WeightPresetManager (FR-4.4)

- **책임:** 조장이 UI에서 선택할 수 있는 3가지 가중치 프리셋을 관리하고, 커스텀 가중치의 합계 유효성을 검증한다. UI 표시 단위는 **퍼센트(%)** 이며, 내부 연산은 0.0~1.0 소수로 수행한 뒤 View에서 ×100 변환하여 표시한다.
- **프리셋 상수 (Git, 문서, 메신저 순서):**

  | 프리셋명 | Git | 문서 | 메신저 |
  | :--- | :--- | :--- | :--- |
  | 개발 중심 | 60% | 25% | 15% |
  | 기획 중심 | 20% | 60% | 20% |
  | 균형 설정 | 40% | 40% | 20% |

- **시그니처:**
  ```python
  class WeightPresetManager:
      PRESETS: dict[str, tuple[float, float, float]]
      def validate_sum(self, w_git: float, w_doc: float, w_msg: float) -> bool:
          """합 1.0(=100%) 여부 검증. 부동소수점 오차 ±0.0001 허용."""
      def preset_names(self) -> list[str]: ...
      def get_preset(self, name: str) -> dict[str, float]:
          """프리셋명 → {"git","doc","msg"}."""
      def match_preset(self, w_git, w_doc, w_msg) -> str | None:
          """현재 가중치와 일치하는 프리셋명 역추적(없으면 None=사용자 조정)."""
      @staticmethod
      def clamp(value: float) -> float:  """[0.0, 1.0] 제한."""
      def normalize(self, weights: dict[str, float]) -> dict[str, float]:
          """음수 0 처리 후 합 1.0으로 비례 정규화(합 0이면 균등 분배)."""
      def redistribute(self, changed_key: str, new_value: float, current: dict) -> dict[str, float]:
        """UI 실시간 연동 지원: 한 축(changed_key)을 new_value로 변경 시,
           나머지 두 축을 기존 비율대로 **동일 비율로** 비례 재분배해 합 1.0(=100%) 유지.
           나머지 합이 0이면 잔여를 균등 분배.
           반올림 잔차는 마지막 축이 흡수한다."""
  ```
- **알고리즘:**
  - `validate_sum()`: `abs(w_git + w_doc + w_msg - 1.0) < 0.0001`이면 `True`.
  - `normalize()`: 각 값을 `max(0, v)`로 보정 후 합으로 나눠 비례 축소한다(상한 클램프는 하지 않아 임의 양수 크기 입력도 처리). 합이 0이면 1/3 균등 분배. 소수 4자리 반올림 후 잔차를 마지막 축에 흡수해 합을 정확히 1.0으로 맞춘다.
  - `redistribute()`: 변경 축을 `clamp(new_value)`로 고정하고, 잔여(`1 - fixed`)를 나머지 두 축의 **기존 비율(각 값 / 나머지 합)대로 동일 비율로** 배분한다. 이로써 하나의 슬라이더를 조절하면 나머지 슬라이더들이 같은 비율로 증감한다(최댓값 축만 우선 줄어드는 것이 아니라, 모든 나머지 축이 현재 비율을 유지하며 균일하게 조절). 나머지 합이 0이면 잔여를 균등 분배. 잔차는 마지막 축이 흡수한다. 모든 연산은 결정론적이다(NFR-1.3).
  - `match_preset()`: PRESETS를 순회하며 ±0.0001 이내로 일치하는 프리셋명을 반환, 없으면 `None`.
  - UI 연동 (개선사항): View의 AnalysisPanel 슬라이더 값 변경 시 `redistribute`가 즉시 호출되어 나머지 슬라이더 바를 자동으로 비례 연동(갱신)하고, 변경된 수치값을 **퍼센트(%) 단위**로 UI에 텍스트로 실시간 표기한다 (FR-4.4). 합계 표시도 `"합계: 100%"` 형식이다. 합 ≠ 100%일 경우 [분석 시작] 버튼이 비활성화되고 경고 문구가 표시된다.

---

### 2.5 WeightRebalancer (FR-4.3)

- **책임:** 임의의 데이터 소스(Git, 문서, 메신저) 중 일부가 부재(결측)하거나 파싱에 실패(None)한 경우, 분석을 중단하지 않고 가용한 소스들의 상대적 비율을 유지하며 가중치를 1.0으로 재정규화한다.
- **시그니처:**
  ```python
  class WeightRebalancer:
      def rebalance(
          self, weights: dict[str, float], available: set[str]
      ) -> dict[str, float]:
          """결측 소스 가중치 0, 나머지 상대 비율 유지 재정규화. 합 1.0±0.0001."""
  ```
- **알고리즘:**
  1. 결측된 소스(키가 `available`에 없는 항목)의 가중치를 `0.0`으로 설정한다.
  2. 가용 소스의 원래 가중치 합(`available_sum`)을 산출한다.
  3. 각 가용 소스의 가중치를 `w / available_sum`으로 재조정하여 상대 비율을 유지한다.
  4. 가용 소스가 1개인 경우 해당 소스 가중치 = `1.0`, 나머지 = `0.0`.
  5. 가용 소스가 0개인 경우 분석이 차단되며, 메시지 `"분석 가능한 데이터 소스가 없습니다."`가 표시된다 (RR FR-4.3).
- **사후조건:** 반환된 가중치의 합은 `1.0 ± 0.0001`. 동일 입력·조합에 대해 결과가 결정론적으로 산출된다 (NFR-1.3).

---

### 2.6 AliasMapper (FR-1.3)

- **책임:** 파서에서 수집된 다양한 플랫폼 별 원시 식별자(GitHub 이메일, 카카오톡 닉네임, OOXML 작성자 메타 등)를 조장이 지정한 매핑 테이블에 따라 단일 팀원(Person)으로 N:1 병합 처리한다.
- **시그니처:**
  ```python
  class AliasMapper:
      def merge(
          self, raw: dict[str, dict], mapping: dict[str, str]
      ) -> dict[str, dict]:
          """raw = {alias: {지표...}}, mapping = {alias: 팀원명}.
             매핑된 alias들의 지표를 팀원 단위로 합산(N:1).
             mapping에 없는 alias(미매핑)는 결과에서 제외.
             서로 다른 미매핑 alias를 임의 병합하지 않는다."""
  ```
- **알고리즘:**
  1. `mapping`에 등록된 각 alias의 지표 데이터를 해당 팀원 키로 합산한다.
  2. `mapping`에 등록되지 않은 **미매핑 식별자**의 데이터는 결과에서 자동 제외한다.
  3. 서로 다른 미매핑 식별자를 시스템이 임의로 병합하지 않는다.
- **호출 방식 (FR-1.3 개정, Controller Design v1.1 §4 연동):**
  - **1차 분석:** Controller가 각 식별자를 자기 자신으로 매핑하는 **항등 매핑** `{alias: alias}`를 전달한다. 분석-전 매핑 다이얼로그는 폐기되었으므로, 분석 시점에는 조장의 매핑 입력이 없다.
  - **병합 재집계 (FR-5.7):** 결과 화면에서 조장이 병합 그룹을 제출하면, Controller가 해당 매핑을 전달하여 `AliasMapper.merge`를 재호출한다. 파서는 재실행하지 않으며, Orchestrator가 보유 중인 원시 지표 위에서 호출된다.
- **용어 구분 (RR §1.4):**
  - **Unknown 작성자:** OOXML 메타데이터 자체가 비어 있는 문서의 작성자 분류 (FR-1.2). 단일 정의된 분류이다.
  - **미매핑 식별자:** 입력 소스에서 발견되었으나 조장이 어느 팀원에도 연결하지 않은 식별자. Unknown과 미매핑은 별개로 처리된다.
- **후보 제안 연동:** 병합 매핑의 *초기 추천값*은 `AliasExtractor`(§2.11)가 결정론적으로 제안하며, `AliasMapper`는 조장이 확정한 매핑만 합산한다(제안 ≠ 자동 병합).

---

### 2.7 ContributionAggregator (FR-4.* 통합)

- **책임:** 정규화, 매핑, 가중치 적용, 스케일링 등의 하위 모듈들을 오케스트레이션하여 최종 산출물인 `MemberScore` 인스턴스 리스트를 생성하는 핵심 집계기이다. `AnalysisOrchestrator`(Controller)로부터 호출되며, None 소스는 `WeightRebalancer` 경유로 처리된다 (NFR-3.2).
- **내부 의존:**
  - `Normalizer` — 지표별 Min-Max 정규화
  - `CappingScaler` — Git 추가 라인 Capping 및 로그 스케일
  - `AnomalySignalDetector` — 이상 신호 생성 (점수 미반영)
  - `WeightRebalancer` — 결측 소스 가중치 재조정
  - `AliasMapper` — 식별자 N:1 통합
- **시그니처:**
  ```python
  class ContributionAggregator:
      def aggregate(
          self,
          git: dict[str, CommitStats] | None,
          docs: dict[str, int] | None,
          msgs: dict[str, int] | None,
          weights: dict[str, float],
          doc_details: dict[str, dict] | None = None,   # [v1.7] 문서 세부 지표 {author:{chars,docs,blocks}}
          msg_details: dict[str, dict] | None = None,   # [v1.7] 메신저 세부 지표 {author:{count,chars,hours}}
      ) -> list[MemberScore]:
          """가용 소스만으로 종합 점수 산출(NFR-3.2). None 소스는 WeightRebalancer 경유.
          [v1.7] doc_details/msg_details가 주어지면 레이더 세부 축(dimensions)을 함께 산출한다.
          하위호환: 두 인자 생략 시 git만 세부 축을 가지며(CommitStats에서 직접 산출),
          종합 점수 계산은 종전과 동일하다."""
  ```
- **파이프라인 단계:**
  1. **가용 소스 판별:** `git`, `docs`, `msgs` 중 `None`이 아닌 항목의 키 집합(`available`)을 구성한다.
  2. **가중치 재조정:** `WeightRebalancer.rebalance(weights, available)`를 호출하여 보정된 가중치를 얻는다.
  3. **Capping 적용 (Git):** Git 데이터가 가용한 경우, 각 커밋의 추가 라인에 `CappingScaler.cap()`을 적용한다. Capping이 발생한 커밋을 기록한다.
  4. **로그 스케일 (Git):** Capping 후 합산 추가 라인에 `CappingScaler.log_scale()`을 적용한다.
  5. **정규화:** 각 지표(Git 로그스케일 라인, 문서 글자수, 메신저 유효 발화수)를 `Normalizer.normalize()`로 0~1 척도로 변환한다.
  6. **이상 신호 탐지:** `AnomalySignalDetector.detect_frequency()` 및 `detect_zscore()`를 호출하여 신호를 수집한다. 신호는 `MemberScore.anomaly_flags`에 기록되지만 `total_score` 계산에는 사용되지 않는다 (STR-7, ConOps P5).
  7. **종합 점수 산출:** 정규화된 점수에 보정된 가중치를 곱하여 `raw_total`을 계산한다: `raw_total = git_score * w_git + doc_score * w_doc + msg_score * w_msg`. 그 후 모든 팀원의 `raw_total` 합계를 구하고, 각 개인의 `raw_total`을 이 합계로 나누어 비례 정규화(Proportional Normalization)를 수행한다. 이로써 전체 팀원의 최종 `total_score` 합계가 항상 1.0(100%)이 되도록 보장한다.
  8. **[v1.7] 세부 축(dimensions) 산출:** 가용 소스마다 3개 세부 지표를 각각 `Normalizer.normalize()`로 0~1 정규화하여 `MemberScore.dimensions`에 담는다. Git은 `CommitStats`의 커밋 수/추가 라인(Capping+로그)/삭제 라인(로그)에서, 문서·메신저는 `doc_details`/`msg_details`가 주어진 경우에만 각 3지표를 산출한다(미주어지면 해당 소스 키 생략). 세부 축은 *표시 전용*으로 `total_score`에 반영하지 않는다(STR-7). 결측 소스 키는 포함하지 않아 가용 소스 수에 따라 3·6·9키가 된다.
  9. **MemberScore 조립:** 팀원별로 `MemberScore` 인스턴스를 생성하여 리스트로 반환한다.
- **병합 재집계 경로 (FR-5.7, Controller Design v1.1 §6 연동):** 결과 화면에서 병합 요청이 발생하면, Controller가 `AliasMapper.merge(raw, new_mapping)` 결과를 입력으로 이 메서드를 재호출한다. [v1.7] `doc_details`/`msg_details`도 동일 매핑으로 병합해 함께 전달하므로 세부 축도 재산출된다. 병합 후 팀원 집합이 달라지면 Min-Max 정규화 기준이 재산출된다 (FR-4.1). 이것이 시각적 점수 합산이 아니라 재집계여야 하는 이유이다.
- **출력 소비 방식 (INV-V1):** `aggregate()`의 반환값(`list[MemberScore]`)은 Controller(`AppController.on_analysis_completed`)에서 `dataclasses.asdict()`로 직렬화된 뒤 View에 전달된다. Model 레이어는 이 직렬화에 관여하지 않는다.

---

### 2.8 CacheManager (NFR-2.3, NFR-2.4)

- **책임:** 이전 분석 세션의 결과를 원자적으로 직렬화/역직렬화하여 캐시 파일(`.qce_cache`)로 영속화한다. 원본 파일이 부재한 상태에서도 캐시만으로 이전 분석 결과를 표시할 수 있다 (NFR-2.4).
- **시그니처:**
  ```python
  class CacheManager:
      def save(self, data: dict) -> None:
          """tmp 쓰기 → fsync → os.replace 원자적 커밋. json만."""
      def load(self) -> dict:
          """JSONDecodeError·KeyError 시 캐시 삭제 후 빈 상태 반환."""
  ```
- **제약사항:**
  - (C-8) `pickle` 모듈 사용 전면 금지. 모든 직렬화는 `json` 모듈만 사용한다.
  - (NFR-2.3) 저장 항목 **화이트리스트**: 식별자, 정규화 점수, 타임스탬프, 가중치 설정만 캐시한다. **메시지 본문·소스코드 내용**은 캐시에 포함하지 않는다.
- **알고리즘:**
  - `save()`:
    1. 임시 파일(`.qce_cache.tmp`)에 `json.dump()`로 데이터를 완전히 기록한다.
    2. `os.fsync()`로 디스크 플러시를 보장한다.
    3. `os.replace()`로 기존 캐시를 원자적으로 교체한다.
    4. 정상 완료 후 `.qce_cache.tmp`는 디스크에 잔존하지 않는다.
  - `load()`:
    1. `.qce_cache` 파일이 존재하면 `json.loads()`로 역직렬화를 시도한다.
    2. `JSONDecodeError` 또는 `KeyError` 발생 시 캐시 파일을 삭제하고 빈 `dict`를 반환한다.
    3. 손상 캐시 발견 시 모달 안내: `"캐시 파일이 손상되어 삭제되었습니다. 재분석이 필요합니다."`.
- **캐시 로드 성공 시:** 상태바에 `"캐시 파일에서 이전 분석 결과를 불러왔습니다. (분석 일시: YYYY-MM-DD HH:MM)"` 메시지가 표시된다 (NFR-2.4).

---

### 2.9 ReportExporter (FR-5.2, FR-5.3)

- **책임:** 분석 결과를 `.md` 또는 `.csv` 형식으로 출력한다. 데이터 소스 결측 시 경고 문구를 주입한다.
- **시그니처:**
  ```python
  class ReportExporter:
      def to_markdown(self, scores: list[MemberScore], missing: set[str]) -> str: ...
      def to_csv(self, scores: list[MemberScore], missing: set[str]) -> bytes:
          """utf-8-sig(BOM)로 인코딩."""
  ```
- **알고리즘:**
  - **Markdown 출력:** 마크다운 테이블 구조(헤더 + 행)로 팀원별 점수를 기록한다. `missing`이 비어있지 않으면 하단에 블록쿼트(`>`)로 경고 문구를 추가한다.
  - **CSV 출력:** Excel에서 한글이 깨지지 않도록 **BOM(`\xef\xbb\xbf`)이 포함된 `utf-8-sig`**로 인코딩하여 `bytes`를 반환한다. `missing`이 비어있지 않으면 빈 행 후 `"WARNING"` 행으로 경고 문구를 추가한다.
  - **경고 문구 형식 (FR-5.3):** `⚠ [데이터 소스명] 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다.` (`[데이터 소스명]`은 `"Git"` / `"문서"` / `"메신저"` 중 결측 소스명).
  - **판정 금지 준수 (STR-7, ConOps P5):** 테이블 헤더에 `"종합 지표"` (또는 동의어)를 사용하며, `"최종 평가"` 등 판정 뉘앙스 표현을 사용하지 않는다.

---

### 2.10 NormalizedSignalsTracker (FR-4.2c)

- **책임:** 조장이 신호 카드에서 "정상으로 표시"한 이상 신호를 *세션 내 예외 상태*로 기억하고, 재렌더 시 해당 신호를 화면 표시에서 제외한다. 신호는 애초에 점수에 반영되지 않으므로(STR-7) 본 트래커는 **표시 전용 상태만** 다루며 종합 점수를 재산출하지 않는다. 영속화하지 않는다(세션 한정, OI-1, NFR-2.3 휘발 정책 부합).
- **시그니처:**
  ```python
  class NormalizedSignalsTracker:
      def dismiss(self, author: str, signal_type: str, ref: str = "") -> None: ...
      def restore(self, author: str, signal_type: str, ref: str = "") -> None: ...
      def is_dismissed(self, author: str, signal_type: str, ref: str = "") -> bool: ...
      def clear(self) -> None: """전체 예외 초기화(새 분석 시)."""
      @staticmethod
      def ref_of(detail: dict) -> str: """CAPPING=hash, EW-02=date, ZSCORE=""."""
      def filter_details(self, author: str, details: list[dict]) -> list[dict]: ...
      def apply(self, scores: list[MemberScore]) -> list[MemberScore]:
          """예외 반영한 새 MemberScore 목록 반환(원본 불변)."""
  ```
- **알고리즘:**
  - 예외는 `(author, signal_type, ref)` 3-튜플 집합으로 보관한다. `ref`는 신호 유형별 식별자(CAPPING=커밋 해시, EW-02=일자, ZSCORE=빈 문자열)다. 따라서 한 작성자의 동일 유형 신호가 여럿이어도 *근거 단위*로 개별 정상 처리된다(RR FR-4.2c).
  - `apply()`: 각 `MemberScore`의 `signal_details`에서 예외 항목을 제거하고, 그 결과 *해당 유형의 상세가 모두 사라진 경우에만* `signals` 라벨에서 그 유형을 제거한다. CAPPING/EW-02/ZSCORE 외의 라벨(예: EW-01)은 보존한다. 원본은 변경하지 않고 `dataclasses.replace`로 사본을 만든다.
- **Controller 연동(C-4):** View(`AnomalySignalPanel`)의 `signal_dismissed(author, type, ref)` Signal → `AppController`가 `dismiss()` 호출 후 `apply()` 결과로 결과 화면을 재렌더한다. 재집계(파서·집계 재실행)는 없다. 상세는 `controller-design.md` 참조.

---

### 2.11 AliasExtractor (FR-1.3)

- **책임:** `AliasMapper`(주어진 매핑 합산)의 *전(前) 단계*로, 세 소스의 식별자를 수집하고 결정론적 군집화로 N:1 병합 **후보 그룹을 제안**한다. 자동 병합을 강제하지 않으며(FR-1.3), 결과 화면 병합 다이얼로그의 초기 추천값을 만든다.
- **시그니처:**
  ```python
  class AliasExtractor:
      @staticmethod
      def normalize_key(alias: str) -> str:
          """비교용 정규화: 이메일 로컬파트 추출, 공백·`. _ -` 제거, 소문자."""
      def extract_identifiers(self, git, docs, msgs) -> list[dict]:
          """{raw_id, source, activity} 식별자 목록(소스별 행). (raw_id, source) 정렬."""
      def unique_aliases(self, identifiers: list[dict]) -> list[str]:
          """분류 라벨(Unknown 등) 제외 고유 raw_id 정렬 목록."""
      def suggest_groups(self, aliases: list[str]) -> dict[str, list[str]]:
          """정규화 키가 같은 alias끼리 묶어 {대표명: [alias...]}."""
      def suggest_mapping(self, identifiers: list[dict]) -> dict[str, str]:
          """식별자 목록 → 추천 초기 매핑 {raw_id: 대표명}."""
  ```
- **알고리즘:**
  - `normalize_key()`: 이메일이면 `@` 앞만 취하고, 공백·`._-`를 제거한 뒤 소문자로 변환한다. (예: `DH-Lee`, `dh.lee`, `daehan.lee@x.com`의 로컬파트가 동일 키로 수렴.)
  - `suggest_groups()`: 정규화 키 버킷으로 묶고, 대표명은 그룹 내에서 **(한글 포함 우선 → 길이 큰 순 → 사전순)** 1순위를 택한다. 분류 라벨(`Unknown`/빈 문자열)은 제외한다.
  - 모든 출력은 정렬·결정론적이다(NFR-1.3). 활동 규모(`activity`)는 Git=추가 라인, 문서=글자수, 메신저=발화수로 채운다.
- **Controller 연동(C-4):** Model이므로 View를 모른다. `AppController`가 결과 인물에 대해 `suggest_groups`로 후보(대표명≠원본인 군집)를 만들어 결과 화면(`ResultScreen.set_suggested_mapping` → `AliasMappingDialog.apply_suggested`)에 전달한다. 실제 병합은 조장 확정 시 `AliasMapper`(§2.6)가 수행한다.

---

## 3. 컴포넌트 간 데이터 흐름

Architecture Overview §7에 정의된 파이프라인에서 BusinessLogic 모듈의 위치를 나타낸다.

```
[파서 출력]             [BusinessLogic 레이어]                    [산출물]
                        ┌───────────────────┐
docs: {author: chars} ──┤                   │
git:  {email: Stats}  ──┤  AliasMapper      │──→ 통합 데이터
msgs: {author: count} ──┤                   │         │
                        └───────────────────┘         ▼
                        ┌───────────────────┐  ┌─────────────┐
                        │  CappingScaler    │──│  Normalizer │
                        └───────────────────┘  └──────┬──────┘
                                                      ▼
                        ┌───────────────────┐  ┌─────────────────────┐
                        │ WeightRebalancer  │──│ContributionAggregator│──→ list[MemberScore]
                        └───────────────────┘  └──────────┬──────────┘         │
                        ┌───────────────────┐             │              ┌─────┴─────┐
                        │AnomalySignalDetect│─(신호 전용)──┘              │           │
                        └───────────────────┘                       CacheManager  ReportExporter
```

> **결측 처리 흐름 (FR-4.3):** 임의 소스가 `None`이면 `AliasMapper` 단계에서 누락되고, `WeightRebalancer`가 해당 가중치를 0으로 만든 뒤 나머지를 합 1.0으로 재정규화한다.

---

## 4. 아키텍처 추적성 매트릭스 (BusinessLogic 부문)

| 컴포넌트 | 실현 FR/NFR | 구속 제약 |
| :--- | :--- | :--- |
| Normalizer | FR-4.1 | — |
| CappingScaler | FR-4.2 | — |
| AnomalySignalDetector | FR-4.2, FR-4.2b, FR-4.2d | STR-7, ConOps P5 (판정 금지) |
| NormalizedSignalsTracker | FR-4.2c | STR-7 (점수 비반영), OI-1 (세션 한정) |
| WeightPresetManager | FR-4.4 | — |
| WeightRebalancer | FR-4.3 | — |
| AliasMapper | FR-1.3 | — |
| AliasExtractor | FR-1.3 | NFR-1.3 (결정론), 자동 병합 금지 |
| ContributionAggregator | FR-4.* 통합 | NFR-3.2 (모듈 격리) |
| CacheManager | NFR-2.3, NFR-2.4 | C-8 (pickle 금지, JSON 전용) |
| ReportExporter | FR-5.2, FR-5.3 | STR-7 (판정 금지 용어) |

---

## 5. 문서 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-05-30 | 최초 작성. 9개 BusinessLogic 컴포넌트 상세 설계. | QCE 개발팀 |
| v1.1 | 2026-05-30 | (1) FR-4.2d → FR-4.2c 식별자 통일 (architecture-overview.md v1.1 동기화). (2) 참조 데이터 타입(§1.4) 추가. (3) 설계 불변식(§1.3) 추가 — PyQt6 금지, 파서 직접 import 금지, 판정 금지, 결정론 보장. (4) AliasMapper에 Unknown vs 미매핑 용어 구분 명시. (5) CacheManager에 저장 항목 화이트리스트 및 원자적 쓰기 절차 상세 추가. (6) ReportExporter에 경고 문구 형식 사양 추가. (7) 컴포넌트 간 데이터 흐름도(§3) 추가. (8) 아키텍처 RTM(§4) 추가. (9) 각 클래스에 코드 블록 형태의 시그니처 추가. | QCE 개발팀 |
| **v1.2** | **2026-05-31** | **(1) AliasMapper §2.6에 호출 방식 명시 — 1차 분석=항등 매핑, 병합 재집계=결과 화면 사후 재호출 (FR-1.3 개정, Controller Design v1.1 §4 연동). (2) ContributionAggregator §2.7에 병합 재집계 경로 및 재정규화 필요성 명시 (FR-5.7). (3) ContributionAggregator §2.7에 출력 소비 방식(INV-V1 — asdict 직렬화는 Controller 책임) 명시. (4) 상위 문서 목록에 Controller Design v1.1 추가.** | QCE 개발팀 |
| v1.4 | 2026-06-01 | 레이더 세부 축(view-design v1.7 연동): (1) `MemberScore`에 `dimensions: dict[str,float]` 필드 추가(가용 소스별 3 세부 지표, 표시 전용). (2) §2.7 `aggregate`에 선택적 `doc_details`/`msg_details` 인자 및 파이프라인 8단계(세부 축 산출) 신설, 병합 재집계 시 세부 데이터도 동일 매핑 병합. 세부 지표 정의: Git=커밋수/추가/삭제, 문서=글자수/문서수/구성요소, 메신저=발화수/발화량/시간대. `total_score` 비반영(STR-7) 유지. | QCE 개발팀 |
| **v1.3** | **2026-05-31** | **구 SRS.md 폐지 반영 및 구현분 정합화(A1~A4). (1) §1.4 데이터 타입을 실제 코드 필드명으로 정합화(`raw_chars`·`raw_messages`·`signals`) 및 신규 필드 `signal_details`·`commit_dates`, `CommitStats.commits_list` 추가 + signal_details 원소 구조 명세. (2) §2.3 AnomalySignalDetector에 `detect_capping`·`detect_zscore_detail`·`build_signal_details` 추가, 실현 FR에 FR-4.2·FR-4.2d(Z-Score) 반영. (3) §2.4 WeightPresetManager에 `normalize`·`redistribute`·`match_preset`·`clamp`·`get_preset`·`preset_names` 추가(FR-4.4 보조 연산). (4) **§2.10 NormalizedSignalsTracker 신설(FR-4.2c 예외 처리)** — 번호 체계 4.2c=예외·4.2d=Z-Score (RR v1.5 정합). (5) **§2.11 AliasExtractor 신설(FR-1.3 결정론적 병합 후보 제안)**. (6) §2.6 AliasMapper에 AliasExtractor 후보 제안 연동 명시. (7) §4 RTM에 NormalizedSignalsTracker·AliasExtractor 행 추가. 상세 View 설계는 view-design.md, Controller 배선은 controller-design.md 참조.** | QCE 개발팀 |
| v1.4 | 2026-06-01 | 사용자 피드백(UI/UX 개선) 반영: (1) §1.4 MemberScore 데이터 클래스에 시각화 툴팁 노출용 원시 데이터 필드(raw_additions, raw_chars, raw_messages) 추가. (2) §2.4 WeightPresetManager에 UI 가중치 실시간 비례 연동 및 텍스트 수치 표기를 지원하기 위한 redistribute 메서드의 UI 연동 책임 명시. | QCE 개발팀 |
| **v1.5** | **2026-06-01** | **사용자 피드백(슬라이더 비례 분배 버그·표기 개선) 반영: (1) §2.4 WeightPresetManager `redistribute` 알고리즘 설명에 "나머지 두 축이 같은 비율로 증감"하는 동작을 명확히 기술(최댓값 축만 우선 줄어드는 기존 동작 교정). (2) 가중치 UI 표기 단위를 소수(1.00) 기준에서 퍼센트(100%) 기준으로 변경 — 프리셋 표, validate_sum, 합계 라벨, 경고 문구 포함.** | QCE 개발팀 |
| **v1.6** | **2026-06-01** | **버그 수정(차트 합계 불일치) 반영: §2.7 ContributionAggregator의 파이프라인 7번(종합 점수 산출)에, 팀 전체의 기여도 합계가 항상 1.0(100%)이 되도록 최종적으로 비례 정규화하는 단계를 추가 명시.** | QCE 개발팀 |