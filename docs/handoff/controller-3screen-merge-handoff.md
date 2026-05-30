# [Controller 담당 공유] 3-스크린 + 결과화면 계정 병합 반영 요청

> 김휘중님께 — View 쪽에서 화면 구조와 신원 병합 방식을 바꿔서, **Controller(`AppController`/`AnalysisOrchestrator`)와 `controller-design.md`에 반영이 필요**합니다. 이 파일은 controller-design.md가 팀원 단독 영역이라 제가 직접 수정하지 않고 변경 요청만 정리한 것입니다. 아래 내용을 그대로 AI에 붙여 검토·구현하시면 됩니다.

## 1. 배경 (이미 반영 완료된 상위 문서)

다음 문서들은 이미 갱신되었습니다. controller-design.md(현재 v1.0)만 미반영 상태입니다.

- **RR v1.4** — FR-5.4(3-스크린), FR-5.5(제출 화면), FR-5.6(로딩 화면), FR-5.7(결과 화면 계정 병합) 신설 + FR-1.3 개정
- **view-design.md v1.3** — MainWindow를 `QStackedWidget` 셸로 재구성, SubmitScreen/LoadingScreen/ResultScreen 신설, 신호/슬롯 계약 갱신
- **architecture-overview.md v1.2** — §4 컴포넌트·§5.5·§7 데이터 흐름·§9 RTM에 3-스크린·병합 반영
- **test-cases.md v1.1 / test-plan.md v1.1** — FR-5.4~5.7 TC 및 STAGE 7/8·RTM 갱신

## 2. 무엇이 바뀌었나 (핵심 4가지)

1. **3-스크린 전환.** 앱이 단일 화면이 아니라 **제출(SubmitScreen) → 로딩(LoadingScreen) → 결과(ResultScreen)** 3화면을 `QStackedWidget`으로 전환합니다. 전환 주체는 Controller입니다.
2. **분석-전 매핑 모달 폐기 (FR-1.3 일원화).** 분석 전에 신원 매핑 다이얼로그를 띄우던 흐름이 사라졌습니다. 1차 분석은 매핑 없이 각 식별자를 **독립 인물**로 산출합니다.
3. **결과 화면 계정 병합 (FR-5.7).** 조장이 결과를 보며 동일인의 여러 계정을 1인으로 병합하면, **원시 지표 재집계 → 재정규화**를 거쳐 그래프를 다시 그립니다. (정규화는 팀원 집합 전체에 의존하므로 시각 합산이 아니라 재집계여야 함 — FR-4.1.)
4. **View는 plain dict만 소비 (결정 A·INV-V1).** Controller가 `MemberScore`를 View로 넘기기 직전 `dataclasses.asdict()`로 dict 직렬화해서 push합니다. (View는 `MemberScore` 타입을 import하지 않음.)
   - 참고: View 점수 dict 키 = `MemberScore` 필드명과 동일(author, git_score, doc_score, msg_score, total_score, raw_additions, raw_chars, raw_messages, capping_applied, signals). 키 재매핑 불필요.

## 3. Controller가 구현/조율해야 할 것

### (a) 화면 전환 조율 (FR-5.4)
`MainWindow.show_submit()/show_loading()/show_result()`를 생명주기에 맞춰 호출:
- 기동(캐시 없음) → `show_submit()` / 캐시 단독 로드 → 즉시 `show_result()` (NFR-2.4)
- `analyze_clicked`(합계 1.0) → `show_loading()`
- `completed` → `show_result()` / `failed` → `show_submit()` + 오류 안내
- `new_analysis_requested` → 상태 초기화 → `show_submit()`
- `merge_requested` → `show_loading()` → 재집계 → `show_result()`

### (b) 신호 connect 대상 변경
- **추가:** `SubmitScreen.documents_dropped/git_repo_chosen/messenger_dropped`, `SubmitScreen.analysis_panel.analyze_clicked`(또는 SubmitScreen이 중계), `ResultScreen.merge_requested(dict)`, `ResultScreen.new_analysis_requested()`
- **제거:** `alias_mapping_requested`(분석-전 매핑 모달 신호 — 폐기)
- 입력 드롭 신호의 발신 주체가 MainWindow → **SubmitScreen**으로 이동했습니다.

### (c) 결과 push 직렬화
`on_analysis_completed(scores: list[MemberScore])` 에서 `[dataclasses.asdict(s) for s in scores]`로 변환 후 `ResultScreen.render(score_dicts, missing)` 호출.

### (d) 1차 분석은 항등 매핑
파이프라인 §4 "식별자 통합" 단계에서 AliasMapper에 **항등 매핑(각 식별자=독립 인물)**을 통과시킵니다. (분석-전 매핑 입력 없음.)

### (e) 계정 병합 재집계 (FR-5.7) — 핵심 신규 로직
```
ResultScreen.merge_requested(mapping={alias→member})  # mapping은 합칠 그룹
  → AppController.on_merge_requested(mapping)
  → show_loading()  (NFR-1.2 is_analyzing 가드)
  → 보유 중인 '원시 지표'에 mapping 적용:
        AliasMapper.merge(raw, mapping)            # N:1 합산 (FR-1.3)
        → ContributionAggregator.aggregate(...)    # Capping→Min-Max 정규화→가중치 재조정 = 재정규화
  → completed(scores) → asdict 직렬화 → ResultScreen.render → show_result()
```
- **원시 지표 보유:** 1차 분석에서 수집한 원시 지표(커밋/글자수/발화수)를 세션 동안 Orchestrator/Controller가 보유해야 재집계가 가능합니다. (병합은 파서를 다시 돌리지 않고 보유 원시 지표 + 새 매핑으로 `AliasMapper.merge`부터 재실행.)
- **결정론·중복 가드:** 동일 병합 입력 = 동일 결과(NFR-1.3). 재집계 중 추가 병합 요청은 `is_analyzing` 가드로 차단(NFR-1.2).
- **분리(병합 취소)**도 매핑을 갱신해 동일 경로로 재집계.

## 4. controller-design.md 문서에 반영 제안 (절 단위)

- **§2.1 AppController 책임/시그니처:** 화면 전환 조율, `on_merge_requested(mapping)`, `on_new_analysis_requested()` 추가. `on_analysis_completed`에 asdict 직렬화 명시.
- **§4 데이터 통합 파이프라인:** 3단계(식별자 통합)를 "1차=항등 매핑 / 병합=결과 화면 사후 재집계"로 개정. 분석-전 매핑 모달·배선 폐기 명시.
- **§5 RTM:** FR-5.4·FR-5.7 추가, asdict 직렬화·병합 가드 반영.
- **(신규) §6 결과 화면 계정 병합 재집계 흐름:** 위 (e) 시퀀스 + 원시 지표 보유 + 결정론.
- **헤더/변경이력:** 상위 문서를 Architecture v1.2·RR v1.4·View Design v1.3로, 버전 v1.1로.

## 5. 검증 (test-plan v1.1 기준)
- `integration/test_merge_reaggregation.py` (L2) — 병합 매핑 재집계 시 **다른 팀원 점수도 변동** + 결정론 (TC-FR-5.7-03·05)
- `ui/test_main_window.py` — 화면 전환 (TC-FR-5.4-*)
- 병합 재집계 중 중복 요청 차단 (TC-FR-5.7-06, NFR-1.2)

## 6. 협의 포인트
- Model(`AliasMapper.merge`, `ContributionAggregator.aggregate`)이 **사후 병합 매핑으로 재호출** 가능해야 합니다. (둘 다 김휘중님 Model 영역이라 자체 조율 가능.)
- 원시 지표 보유 위치(`AnalysisOrchestrator` 내 캐싱 vs `AppController`)는 구현 재량.
- View 측 신호/슬롯 시그니처는 view-design.md v1.3 §5.1·§5.2 계약표가 단일 출처입니다. 궁금하면 이대한에게.
