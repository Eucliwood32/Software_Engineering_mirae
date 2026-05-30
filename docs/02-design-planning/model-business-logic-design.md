# Model Business Logic 설계 (Model BusinessLogic Design)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.2 |
| 작성일 | 2026-05-31 |
| 상위 문서 | Architecture Overview v1.2, Requirements Record v1.4, Development Constraints v2.0, Controller Design v1.1 |
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

@dataclass
class MemberScore:                      # FR-4.* 통합 결과
    author: str
    git_score: float                    # 0.0~1.0
    doc_score: float                    # 0.0~1.0
    msg_score: float                    # 0.0~1.0
    total_score: float                  # 0.0~1.0
    raw_additions: int
    raw_char_count: int
    raw_msg_count: int
    capping_applied: bool
    anomaly_flags: list[str] = field(default_factory=list)  # 예: ["EW-02", "ZSCORE"]
```

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

### 2.3 AnomalySignalDetector (FR-4.2b, FR-4.2c)

- **책임:** 통계적·규칙적 이상 징후를 식별하여 조장에게 표시하기 위한 신호를 생성한다. **최종 평가 점수에는 자동 반영되지 않으며** (ConOps P5 판정 금지 원칙, STR-7), 조장의 의사결정을 돕는 보조 지표로만 사용된다. 신호는 혐의 제기가 아니라 **검증 권유**이다 (ConOps §7.2).
- **시그니처:**
  ```python
  class AnomalySignalDetector:
      def detect_frequency(self, repo: dict[str, CommitStats]) -> list[dict]:
          """작성자 단기 커밋 빈도가 평소 일평균의 3배 초과 구간을 신호로.
             반환: [{author, period, period_commits, baseline_avg}, ...]"""
      def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
          """정규화 지표 Z-Score ≤ -1.5가 2개 이상인 팀원명 리스트."""
  ```
- **알고리즘:**
  - `detect_frequency()` (EW-02): 작성자별 일자별 커밋 시계열을 구성하여, 특정 일자의 커밋 수가 해당 작성자의 일평균 커밋 수의 3배를 초과하는 구간을 식별한다. 각 신호 항목은 `author`, `period`, `period_commits`, `baseline_avg`를 포함한다.
  - `detect_zscore()` (FR-4.2c): 정규화된 지표(Git, 문서, 메신저)에 대해 팀원별 Z-Score를 산출하고, Z-Score가 -1.5 이하인 항목이 2개 이상 존재하는 팀원의 이름을 리스트로 반환한다. 신호 대상 팀원은 산점도(FR-5.1c)에서 붉은색 + ⚠ 오버레이로 강조 표시된다.
- **격리 원칙:** 이 클래스의 출력은 `MemberScore.anomaly_flags`에 기록되지만, `total_score` 계산 경로에는 투입되지 않는다.

---

### 2.4 WeightPresetManager (FR-4.4)

- **책임:** 조장이 UI에서 선택할 수 있는 3가지 가중치 프리셋을 관리하고, 커스텀 가중치의 합계 유효성을 검증한다.
- **프리셋 상수 (Git, 문서, 메신저 순서):**

  | 프리셋명 | Git | 문서 | 메신저 |
  | :--- | :--- | :--- | :--- |
  | 개발 중심 | 0.60 | 0.25 | 0.15 |
  | 기획 중심 | 0.20 | 0.60 | 0.20 |
  | 균형 설정 | 0.40 | 0.40 | 0.20 |

- **시그니처:**
  ```python
  class WeightPresetManager:
      PRESETS: dict[str, tuple[float, float, float]]
      def validate_sum(self, w_git: float, w_doc: float, w_msg: float) -> bool:
          """합 1.0 여부 검증. 부동소수점 오차 ±0.0001 허용."""
  ```
- **알고리즘:** `abs(w_git + w_doc + w_msg - 1.0) < 0.0001`이면 `True`, 아니면 `False`.
- **UI 연동:** 합 ≠ 1.0일 경우 View의 [분석 시작] 버튼이 비활성화되고, 경고 문구 `"가중치 합계가 1.00이어야 합니다. 현재: X.XX"`가 표시된다 (RR FR-4.4). 슬라이더 step은 0.05 단위.

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
      ) -> list[MemberScore]:
          """가용 소스만으로 종합 점수 산출(NFR-3.2). None 소스는 WeightRebalancer 경유."""
  ```
- **파이프라인 단계:**
  1. **가용 소스 판별:** `git`, `docs`, `msgs` 중 `None`이 아닌 항목의 키 집합(`available`)을 구성한다.
  2. **가중치 재조정:** `WeightRebalancer.rebalance(weights, available)`를 호출하여 보정된 가중치를 얻는다.
  3. **Capping 적용 (Git):** Git 데이터가 가용한 경우, 각 커밋의 추가 라인에 `CappingScaler.cap()`을 적용한다. Capping이 발생한 커밋을 기록한다.
  4. **로그 스케일 (Git):** Capping 후 합산 추가 라인에 `CappingScaler.log_scale()`을 적용한다.
  5. **정규화:** 각 지표(Git 로그스케일 라인, 문서 글자수, 메신저 유효 발화수)를 `Normalizer.normalize()`로 0~1 척도로 변환한다.
  6. **이상 신호 탐지:** `AnomalySignalDetector.detect_frequency()` 및 `detect_zscore()`를 호출하여 신호를 수집한다. 신호는 `MemberScore.anomaly_flags`에 기록되지만 `total_score` 계산에는 사용되지 않는다 (STR-7, ConOps P5).
  7. **종합 점수 산출:** 정규화된 점수에 보정된 가중치를 곱하여 `total_score`를 계산한다: `total = git_score * w_git + doc_score * w_doc + msg_score * w_msg`.
  8. **MemberScore 조립:** 팀원별로 `MemberScore` 인스턴스를 생성하여 리스트로 반환한다.
- **병합 재집계 경로 (FR-5.7, Controller Design v1.1 §6 연동):** 결과 화면에서 병합 요청이 발생하면, Controller가 `AliasMapper.merge(raw, new_mapping)` 결과를 입력으로 이 메서드를 재호출한다. 인터페이스는 변경되지 않으며, 병합 후 팀원 집합이 달라지면 Min-Max 정규화 기준이 재산출된다 (FR-4.1). 이것이 시각적 점수 합산이 아니라 재집계여야 하는 이유이다.
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
| AnomalySignalDetector | FR-4.2b, FR-4.2c | STR-7, ConOps P5 (판정 금지) |
| WeightPresetManager | FR-4.4 | — |
| WeightRebalancer | FR-4.3 | — |
| AliasMapper | FR-1.3 | — |
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
