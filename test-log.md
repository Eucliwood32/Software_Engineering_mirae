# Test Log — QCE 부탁해 꼬마선장

| 항목 | 내용 |
|---|---|
| 작성일 | 2026-05-29 |
| 담당 | 조원희 (STAGE 0 ~ 3) |
| 기준 문서 | `docs/03-verification-validation/test-plan.md` v1.0, `test-cases.md` v1.0 |
| 실행 환경 | Python 3.12.4 · pytest 9.0.3 · Windows 10 x64 |

---

## 1. 환경 구축

### 생성 파일

| 파일 | 내용 |
|---|---|
| `pytest.ini` | `testpaths=tests`, `pythonpath=.`, `-q` 기본 옵션 |
| `qce/` | 29개 빈 패키지 스텁 (model/parsing, model/business, controller, view) |
| `tests/conftest.py` | `tmp_docx`, `git_repo`, `katalk` 픽스처 + `_no_network` autouse |
| `tests/fixtures/factories.py` | `make_docx/pptx/hwpx/corrupted/empty_docx`, `make_git_repo`, `make_katalk`, `sample_scores` 팩토리 |

### requirements.txt 추가 패키지

`charset-normalizer` — `EncodingHandler`에서 Shift-JIS 감지에 필요 (pip에 이미 포함되어 있음, 별도 설치 불필요).

---

## 2. STAGE 0 — 정적 게이트 골격

**원칙:** 빈 패키지에 대해 위반 0건 → 전부 GREEN.

| 테스트 파일 | 케이스 수 | 검증 내용 |
|---|:---:|---|
| `tests/static/test_forbidden_imports.py` | 3 | 금지 import(requests·urllib·httpx·socket·http.client·pickle), JRE(konlpy·jpype), requirements.txt JRE 부재 |
| `tests/static/test_mvc_layering.py` | 3 | View→Model 직접 import 금지, Model에 PyQt6 import 금지, 파서 상호 import 금지 |
| `tests/static/test_no_jre_dep.py` | 2 | konlpy·jpype·jpype1 소스 전체 0건, pickle 0건 |
| `tests/static/test_readonly_input.py` | 1 | 분석 모듈의 쓰기 모드 open 탐지 (화이트리스트: report_exporter, cache_manager) |

**결과:** 9/9 GREEN (0.05s)

---

## 3. STAGE 1 — 순수 타입·수학

### 구현 파일

| 파일 | 주요 내용 |
|---|---|
| `qce/model/types.py` | `CommitStats`, `MessengerRecord`, `ParseResult`, `MemberScore` 데이터클래스 |
| `qce/model/business/normalizer.py` | Min-Max 정규화, zero-variance → 0.5, round(4자리) |
| `qce/model/business/capping_scaler.py` | `cap(n)`: `n>1000 → (1000,True)`, `math.log1p` |
| `qce/model/business/weight_preset_manager.py` | 3개 프리셋(개발/기획/균형), `validate_sum` |
| `qce/model/business/weight_rebalancer.py` | 결측 소스 0처리 + 상대 비율 재정규화, 합 1.0±0.0001 |

### 테스트 결과

| 파일 | 케이스 수 | 결과 |
|---|:---:|:---:|
| `test_normalizer.py` | 7 | GREEN |
| `test_capping_scaler.py` | 7 | GREEN |
| `test_weight_preset_manager.py` | 6 | GREEN |
| `test_weight_rebalancer.py` | 5 | GREEN |

**누적:** 34/34 GREEN

---

## 4. STAGE 2 — 파싱 인프라

### 구현 파일

| 파일 | 주요 내용 |
|---|---|
| `qce/model/parsing/encoding_handler.py` | UTF-8→CP949 순 시도, charset-normalizer로 cp932(Shift-JIS) 등 사전 거부 |
| `qce/model/business/alias_mapper.py` | `{alias: 지표}` N:1 합산, 미매핑 제외, Unknown≠미매핑 구분 |

### 트러블슈팅

**문제:** `"テスト".encode("shift_jis")` 바이트가 `errors="strict"` CP949 디코딩에서도 예외 없이 통과됨.

**원인:** Shift-JIS 바이트 `\x83\x65\x83\x58\x83\x67`이 CP949의 유효한 2바이트 시퀀스에 해당.

**해결:** `charset-normalizer`가 Shift-JIS를 `cp932`로 감지 → `_REJECT_FAMILIES` 집합에 포함하여 사전 거부.

### 테스트 결과

| 파일 | 케이스 수 | 결과 |
|---|:---:|:---:|
| `test_encoding_handler.py` | 4 | GREEN |
| `test_alias_mapper.py` | 5 | GREEN |

**누적:** 43/43 GREEN

---

## 5. STAGE 3 — 소스 파서 5종

### 구현 파일

| 파일 | 주요 내용 |
|---|---|
| `qce/model/parsing/document_parser.py` | `.docx`(python-docx) / `.pptx`(python-pptx) / `.hwpx`(zipfile+ElementTree) 파싱, 손상 파일 `{}` 반환 |
| `qce/model/parsing/git_analyzer.py` | `git log --numstat --format=%H\|%ae\|%ai`, CalledProcessError·TimeoutExpired → `{}` |
| `qce/model/parsing/git_health_checker.py` | `git --version` timeout 5s, 반환코드 0 여부 |
| `qce/model/parsing/messenger_parser.py` | test-plan §4.3 형식 계약 정규식, EncodingHandler 경유, 오염줄 skip 카운트 |
| `qce/model/parsing/stopword_filter.py` | 미디어 태그·자음 리액션·1글자 응답 패턴, 사용자 편집 API 없음 |

### 트러블슈팅

**문제:** `author=None`으로 `make_docx` 호출 시 `core_properties.author`가 `"python-docx"` 기본값으로 설정됨.

**해결:** `tests/fixtures/factories.py`의 `make_docx`에서 `author=None`일 때 `""` 명시 설정.

### 테스트 결과

| 파일 | 케이스 수 | 결과 |
|---|:---:|:---:|
| `test_document_parser.py` | 11 | GREEN |
| `test_git_analyzer.py` | 5 | GREEN |
| `test_git_health_checker.py` | 4 | GREEN |
| `test_messenger_parser.py` | 9 | GREEN |
| `test_stopword_filter.py` | 6 | GREEN |

**누적: 78/78 GREEN (1.74s)**

---

## 6. 현재 상태 요약

```
pytest tests/unit tests/static -q
78 passed in 1.74s
```

### 완료된 구현

```
qce/model/types.py                         ← CommitStats, MessengerRecord, ParseResult, MemberScore
qce/model/parsing/encoding_handler.py      ← NFR-3.1
qce/model/parsing/document_parser.py       ← FR-1.1/1.2
qce/model/parsing/git_analyzer.py          ← FR-2.1
qce/model/parsing/git_health_checker.py    ← FR-2.2 로직
qce/model/parsing/messenger_parser.py      ← FR-3.1/3.2
qce/model/parsing/stopword_filter.py       ← FR-3.3
qce/model/business/normalizer.py           ← FR-4.1
qce/model/business/capping_scaler.py       ← FR-4.2
qce/model/business/weight_preset_manager.py← FR-4.4 로직
qce/model/business/weight_rebalancer.py    ← FR-4.3
qce/model/business/alias_mapper.py         ← FR-1.3
```

### 미구현 (빈 스텁)

```
qce/model/business/anomaly_signal_detector.py  ← FR-4.2b/4.2d  (STAGE 4, 김휘중)
qce/model/business/contribution_aggregator.py  ← FR-4.* 통합   (STAGE 4, 김휘중)
qce/model/business/cache_manager.py            ← NFR-2.3/2.4   (STAGE 5, 김휘중)
qce/model/business/report_exporter.py          ← FR-5.2/5.3    (STAGE 5, 김휘중)
qce/controller/analysis_orchestrator.py        ← NFR-1.1/1.2   (STAGE 6, 이대한)
qce/controller/app_controller.py               ← 라우팅         (STAGE 6, 이대한)
qce/view/ (전체)                                ← STAGE 7, 이대한
```

---

## 7. 다음 단계

| STAGE | 담당 | 내용 |
|---|---|---|
| STAGE 4~5 | 김휘중 | `AnomalySignalDetector`, `ContributionAggregator`, `CacheManager`, `ReportExporter` |
| STAGE 6~7 | 이대한 | `AnalysisOrchestrator`, `AppController`, View 전체 (차트 3종, 다이얼로그) |
| STAGE 8 | 전체 | 통합 테스트 (`tests/integration/`, `tests/ui/`) |
| 빌드 | 전체 | PyInstaller → `QCE.exe` |

지침서: `docs/03-verification-validation/ai-tdd-guide.md` 참조.
