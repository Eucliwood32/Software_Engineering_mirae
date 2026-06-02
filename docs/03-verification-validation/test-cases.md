# Test Cases
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.3 |
| 작성일 | 2026-06-01 |
| 상위 문서 | `test-plan.md` v1.3, Requirements Record v1.6, Architecture Overview v1.3 |
| 작성 주체 | QCE 개발팀 |

---

## 0. 케이스 표기 규약

각 케이스는 다음을 갖는다.

- **TC-ID:** `TC-<FR/NFR>-<순번>`. (예: `TC-FR-4.1-03`)
- **P(우선순위):** `P0`(핵심·차단) / `P1`(중요) / `P2`(부가).
- **L(레벨):** L0 정적 / L1 단위 / L2 통합 / L3 UI / L4 수동.
- **판정:** 명시된 기대값과 `==` 또는 명시된 허용오차(`±0.0001`, `±0.001`)로 비교. 그 외 모호성 없음.

> 각 절 머리의 **계약 블록**은 구현해야 할 시그니처/반환을 못 박는다. 케이스는 그 계약 위에서 정의된다. `# FR-x.y` 주석은 코드/커밋에 그대로 박는다(INDEX.md 기여자 가이드).

> **공통 픽스처**는 `test-plan.md §5`(conftest)와 §4(팩토리)를 참조. 본 문서는 그 위에서 입력/기대만 기술한다.

---

# FR-1. 통합 입력 — 문서

### 계약 (DocumentParser, architecture §5.2)
```python
class DocumentParser:                       # FR-1.1, FR-1.2
    def parse(self, path: str) -> dict[str, int]:
        """확장자에 따라 .pptx/.docx/.hwpx 추출기로 위임.
           반환 {작성자식별자: 공백·개행 제외 유효 글자수}.
           메타 부재 → 'Unknown' 키. 손상 파일 → 예외 대신 호출측에 skip 통지."""
    def count_shapes(self, path: str) -> int:
        """문서 내 도형(텍스트박스 포함) 개수."""
```
작성자 규칙: **docx → `core_properties.author`**, **pptx → `core_properties.last_modified_by`**, **hwpx → 표준 메타 작성자**. 글자수 = `len(text.replace(' ','').replace('\n',''))`(탭·기타 공백도 제외 권장).

## FR-1.1 글자수·도형 추출

| TC-ID | P | L | 입력(픽스처) | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-1.1-01 | P0 | L1 | `make_docx(author="A", text="가"*200)` | `parse()`의 값 합 == **200** (±0) | 200자 docx |
| TC-FR-1.1-02 | P0 | L1 | `make_pptx(slides=[["가"*50,"나"*50]]*3)` (3슬라이드×2박스×50) | 글자수 합 **300**, `count_shapes()` == **6** | 슬라이드 규칙 |
| TC-FR-1.1-03 | P0 | L1 | `make_hwpx(author="A", text="다"*200)` | 글자수 **200**±0 | HWPX 지원 |
| TC-FR-1.1-04 | P0 | L1 | 한 폴더에 .docx/.pptx/.hwpx 각 1개 | 세 형식 모두 추출 성공(각자 기대값 일치) | 혼재 입력 |
| TC-FR-1.1-05 | P0 | L1 | `make_empty_docx()` | 글자수 **0**, 도형 **0**, 예외 없음 | 빈 파일 |
| TC-FR-1.1-06 | P0 | L1 | `make_corrupted("x.docx")` | 예외 전파 없음, 해당 파일 skip, 경고에 **파일명 포함** | 손상 skip |
| TC-FR-1.1-07 | P1 | L1 | 글자 사이 공백·개행 다수(`"가 나\n다"`) | 공백·개행 제외 글자수만 카운트(=3) | 유효 글자 정의 |

```python
# tests/unit/model/parsing/test_document_parser.py
def test_docx_200_chars(tmp_docx):                       # TC-FR-1.1-01
    p = tmp_docx("Alice", "가"*200)
    assert sum(DocumentParser().parse(p).values()) == 200

def test_pptx_chars_and_shapes(tmp_path):                # TC-FR-1.1-02
    from tests.fixtures.factories import make_pptx
    p = make_pptx(str(tmp_path/"s.pptx"), "Bob", [["가"*50,"나"*50]]*3)
    dp = DocumentParser()
    assert sum(dp.parse(p).values()) == 300
    assert dp.count_shapes(p) == 6

def test_corrupted_is_skipped(tmp_path):                 # TC-FR-1.1-06
    from tests.fixtures.factories import make_corrupted
    p = make_corrupted(str(tmp_path/"bad.docx"))
    # 손상 통지 방식은 구현 계약에 맞춰 검증(예: parse가 {} 또는 skip 신호 반환).
    # 핵심: 예외가 호출자로 전파되지 않는다.
    result = DocumentParser().parse(p)   # must not raise
    assert isinstance(result, dict)
```

## FR-1.2 작성자별 집계

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-1.2-01 | P0 | L1 | docx(A,100자) + docx(Bob,150자) 두 파일 집계 | `{"Alice":100,"Bob":150}` | 작성자 집계 |
| TC-FR-1.2-02 | P0 | L1 | `make_docx(author=None, text="x"*30)` | 결과에 `"Unknown"` 키 존재, 예외 없음 | 메타 부재 |
| TC-FR-1.2-03 | P1 | L1 | pptx(last_modified_by="Carol") | 키가 "Carol"(pptx는 last_modified_by) | 작성자 출처 규칙 |
| TC-FR-1.2-04 | P1 | L1 | "Unknown"(메타부재) vs 미매핑(FR-1.3)은 별개 | Unknown은 단일 분류로 유지, 병합 안 됨 | 용어 구분 |

## FR-1.3 신원 매핑 (AliasMapper)

### 계약
```python
class AliasMapper:                          # FR-1.3
    def merge(self, raw: dict[str, dict], mapping: dict[str, str]) -> dict[str, dict]:
        """raw = {alias: {지표...}}, mapping = {alias: 팀원명}.
           매핑된 alias들의 지표를 팀원 단위로 합산(N:1).
           mapping에 없는 alias(미매핑)는 결과에서 제외.
           서로 다른 미매핑 alias를 임의 병합하지 않는다."""
```

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-1.3-01 | P0 | L1 | raw 3 alias({dh-lee, daehan.lee, 이대한}) → 모두 "이대한" | 단일 인격으로 지표 합산 | N:1 합산 |
| TC-FR-1.3-02 | P0 | L1 | mapping에 없는 alias 1개 포함 | 그 alias 결과에서 제외 | 미매핑 제외 |
| TC-FR-1.3-03 | P0 | L1 | 미매핑 alias 2개(서로 다름) | 자동 병합 안 됨(각자 독립 제외) | 임의 병합 금지 |
| TC-FR-1.3-04 | P1 | L1 | "Unknown"(FR-1.2) + 미매핑 alias 공존 | 둘을 동일 취급하지 않음 | Unknown≠미매핑 |
| TC-FR-1.3-05 | P1 | L2 | 매핑 UI 노출 식별자 = 전 소스 union | 누락 alias 0개(UI 데이터 계약) | 빠짐없이 제시 |

`AliasExtractor`(결정론적 병합 후보 제안, 자동 병합 아님) 및 다이얼로그 추천 적용:

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-1.3-06 | P0 | L1 | `normalize_key("DH-Lee")`, `"dh.lee"`, `"daehan.lee@x.com"` | 앞 둘 동일 키 / 셋째 로컬파트 추출 | 정규화 |
| TC-FR-1.3-07 | P0 | L1 | `suggest_groups(["dh-lee","dh.lee","DH LEE"])` | 한 그룹(한글 우선·길이·사전순 대표) | 군집 제안 |
| TC-FR-1.3-08 | P1 | L1 | `suggest_groups(["Unknown","alice"])` | Unknown 제외, alice 단독 | 라벨 제외 |
| TC-FR-1.3-09 | P1 | L3 | `apply_suggested({"dh-lee":"이대한",...})` (멤버에 존재) | 해당 행 드롭다운 미리 선택, 대표명==raw_id 행은 미선택 | 추천 기본값 |

```python
def test_suggest_groups_clusters_similar():               # TC-FR-1.3-07
    groups = AliasExtractor().suggest_groups(["dh-lee","dh.lee","DH LEE"])
    assert len(groups) == 1

def test_n_to_1_merge():                                  # TC-FR-1.3-01
    raw = {"dh-lee":{"add":10}, "daehan.lee":{"add":5}, "이대한":{"add":3}}
    mapping = {"dh-lee":"이대한","daehan.lee":"이대한","이대한":"이대한"}
    out = AliasMapper().merge(raw, mapping)
    assert out["이대한"]["add"] == 18 and len(out) == 1

def test_unmapped_excluded():                             # TC-FR-1.3-02/03
    raw = {"a":{"add":1}, "ghost1":{"add":9}, "ghost2":{"add":7}}
    out = AliasMapper().merge(raw, {"a":"Alice"})
    assert "Alice" in out and "ghost1" not in out and "ghost2" not in out
```

---

# FR-2. 통합 입력 — Git

### 계약 (GitAnalyzer, GitHealthChecker)
```python
class GitAnalyzer:                          # FR-2.1
    GIT_TIMEOUT: int = 30
    def analyze(self, repo_path: str) -> dict[str, CommitStats]:
        """git log --numstat --format='%H|%ae|%ai' 파싱.
           {author_email: CommitStats(commits, additions, deletions)}.
           잘못된 경로/실패 → {} 반환(CalledProcessError·FileNotFoundError 비전파)."""

class GitHealthChecker:                      # FR-2.2
    def is_available(self) -> bool:
        """git --version (timeout 5s). FileNotFoundError 또는 returncode!=0 → False."""
```

## FR-2.1 Git 로그 추출

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-2.1-01 | P0 | L1 | `git_repo([{email:alice@test.com, add:10, del:5}])`(측정 커밋만) | `{"alice@test.com": CommitStats(1,10,5)}` 정확 일치 | 정확 매치 |
| TC-FR-2.1-02 | P0 | L1 | 존재하지 않는 경로 문자열 | `{}`, 예외 없음 | 잘못된 경로 |
| TC-FR-2.1-03 | P1 | L1 | 빈 디렉토리(git init 안 함) | `{}`, 예외 없음 | FileNotFoundError류 흡수 |
| TC-FR-2.1-04 | P1 | L1 | 2명 author 혼합 커밋 | author별 분리 집계 | 멀티 author |
| TC-FR-2.1-05 | P2 | L1 | 50,000 커밋 repo | 30초 이내 완료(timeout 미발동) | 성능 |
| TC-FR-2.1-06 | P1 | L1 | timeout 강제(Mock subprocess `TimeoutExpired`) | `{}` 반환, 비정상 종료 없음 | 타임아웃 처리 |

```python
def test_git_exact_stats(git_repo):                        # TC-FR-2.1-01
    repo = git_repo([
        {"email":"base@x.com","date":"2024-01-01 00:00:00","add":100,"del":0},   # 베이스(측정 제외 대상)
        {"email":"alice@test.com","date":"2024-01-02 00:00:00","add":10,"del":5},
    ])
    stats = GitAnalyzer().analyze(repo)
    a = stats["alice@test.com"]
    assert (a.commits, a.additions, a.deletions) == (1, 10, 5)

def test_git_bad_path_returns_empty():                     # TC-FR-2.1-02
    assert GitAnalyzer().analyze("/no/such/repo/xyz") == {}

def test_git_timeout(monkeypatch):                         # TC-FR-2.1-06
    import subprocess
    def boom(*a, **k): raise subprocess.TimeoutExpired(cmd="git", timeout=30)
    monkeypatch.setattr(subprocess, "run", boom)
    assert GitAnalyzer().analyze(".") == {}
```

## FR-2.2 Git 부재 시 안내 (헬스체크 로직 + 다이얼로그)

**로직(L1):**

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-2.2-01 | P0 | L1 | Mock: `git --version` → `FileNotFoundError` | `is_available()` == False | 미설치 감지 |
| TC-FR-2.2-02 | P0 | L1 | Mock: returncode 1 | False | 비정상 코드 |
| TC-FR-2.2-03 | P0 | L1 | Mock: returncode 0, "git version 2.x" | True | 정상 |
| TC-FR-2.2-04 | P1 | L1 | Mock: `TimeoutExpired`(5s) | False, 예외 없음 | 헬스체크 timeout |

**다이얼로그(L3, pytest-qt):**

| TC-ID | P | L | 절차 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-2.2-05 | P0 | L3 | is_available=False로 앱 기동 | **메인 윈도우 표시 전** 모달 출현 | 표시 순서 |
| TC-FR-2.2-06 | P0 | L3 | 모달 텍스트 검사 | "Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다." 포함 | 문구 |
| TC-FR-2.2-07 | P0 | L3 | 모달 링크 클릭 → `webbrowser.open` Mock | 인자가 `https://git-scm.com/download/win` | 링크 |
| TC-FR-2.2-08 | P1 | L3 | 모달 본문 | PATH 설정 안내 1줄 이상 포함 | PATH 안내 |
| TC-FR-2.2-09 | P0 | L3 | [확인] 클릭 | 앱 계속 실행, Git 기능만 비활성 | 우회 동작 |
| TC-FR-2.2-10 | P0 | L3 | is_available=True | 모달 미표시 | 정상 환경 |

```python
def test_health_missing(monkeypatch):                      # TC-FR-2.2-01
    import subprocess
    monkeypatch.setattr(subprocess, "run",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    assert GitHealthChecker().is_available() is False

def test_dialog_opens_link(qtbot, monkeypatch):            # TC-FR-2.2-07
    calls = []
    import webbrowser; monkeypatch.setattr(webbrowser, "open", lambda u: calls.append(u))
    dlg = GitMissingDialog(); qtbot.addWidget(dlg)
    dlg.download_button.click()
    assert calls == ["https://git-scm.com/download/win"]
```

---

# FR-3. 통합 입력 — 메신저 (카카오톡 단독)

### 계약 (MessengerParser, StopwordFilter)
```python
class MessengerParser:                      # FR-3.1, FR-3.2
    def parse(self, path: str) -> ParseResult:   # ParseResult(records, skipped_lines)
        """카톡 .txt → records[MessengerRecord(author,timestamp,message)].
           §test-plan 4.3 형식 계약. 오염 줄 skip + 카운트. 인코딩은 EncodingHandler 경유."""

class StopwordFilter:                        # FR-3.3
    def count_valid_messages(self, records: list[MessengerRecord]) -> dict[str, int]:
        """자동 불용어 제외 후 {author: 유효 메시지 수}. 결정론·사용자 편집 미제공."""
```

## FR-3.1 카카오톡 파싱

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-3.1-01 | P0 | L1 | 정상 발화 3줄(`[A][..]m1`,`[B]..`,`[A]..`) | records 3, author/message 정확 분리 | 정확 파싱 |
| TC-FR-3.1-02 | P0 | L1 | UTF-8 한글 메시지 | 한글 무손상 | UTF-8 |
| TC-FR-3.1-03 | P0 | L1 | `katalk(enc="cp949")` 한글 메시지 | 한글 무손상 | CP949 |
| TC-FR-3.1-04 | P1 | L1 | 날짜 구분줄 포함 | 날짜줄은 record 아님(발화만 records) | 형식 계약 |
| TC-FR-3.1-05 | P1 | L1 | 메시지에 콜론·대괄호 포함 | author/message 경계 정확(첫 패턴만) | 경계 견고성 |
| TC-FR-3.1-06 | P0 | L2 | 카카오톡 로그만 입력(Git·문서 없음) | 앱이 멈추지 않고 파이프라인 정상 작동, 분석 결과 화면 표시 | 카톡 단독 분석 |
| TC-FR-3.1-07 | P0 | L2 | 카카오톡 로그 파싱 후 매핑 화면 | 추출된 모든 발화자 식별자가 병합(매핑) 목록에 누락 없이 표출 | 식별자 매핑 100% |

```python
def test_katalk_standalone_pipeline(katalk):                # TC-FR-3.1-06
    """카카오톡만 입력해도 파이프라인이 정상 동작하고 분석 화면이 표시된다."""
    path = katalk([("A","회의 시작"), ("B","확인"), ("A","수고")])
    # Orchestrator에 msg만 전달, git=None, docs=None
    result = AnalysisOrchestrator().run(git_path=None, doc_paths=[], msg_path=path,
                                        weights={"git":0.4,"doc":0.4,"msg":0.2})
    assert result is not None  # 결과가 반환됨(빈 화면이 아님)
    assert any(s.author in ("A","B") for s in result)

def test_katalk_identifiers_in_mapping(katalk):             # TC-FR-3.1-07
    """카톡에서 추출된 발화자가 매핑 후보에 빠짐없이 표출된다."""
    path = katalk([("Alice","안녕"), ("Bob","ㅇㅇ"), ("Charlie","네")])
    result = MessengerParser().parse(path)
    authors = {r.author for r in result.records}
    # 매핑 후보 목록에 파서가 추출한 모든 author가 포함되어야 함
    assert {"Alice","Bob","Charlie"}.issubset(authors)
```

## FR-3.2 오염 줄 방어적 Skip

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-3.2-01 | P0 | L1 | 정상 10 + 오염 3 | `records==10`, `skipped_lines==3` | 핵심 |
| TC-FR-3.2-02 | P0 | L1 | 전체 100줄 오염 | `records==0`(빈 리스트), `skipped==100`, 예외 없음 | 전량 오염 |
| TC-FR-3.2-03 | P0 | L1 | 빈 파일 | records 0, skipped 0, 예외 없음 | 경계 |
| TC-FR-3.2-04 | P0 | L1 | 위 모든 경우 | 프로세스 종료 없음(return 정상) | 안정성 |

```python
def test_skip_counts(katalk):                              # TC-FR-3.2-01
    lines = [("A","안녕")]*10 + ["@@깨진줄@@","??? not valid","---"]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 10 and res.skipped_lines == 3

def test_all_garbage(katalk):                              # TC-FR-3.2-02
    res = MessengerParser().parse(katalk(["xx"]*100))
    assert res.records == [] and res.skipped_lines == 100
```

## FR-3.3 자동 불용어 처리

불용어 카테고리(RR FR-3.3): **단순 리액션**(`ㅇㅇ ㅋㅋ ㅎㅎ ㄱㄱ ㄴㄴ ㄷㄷ ㅠㅠ` 등 자음·반복), **미디어 태그**(`(이모티콘) (사진) (동영상) (파일)`), **1글자 응답**(`네 예 응 굳`).

| TC-ID | P | L | 입력 메시지들 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-3.3-01 | P0 | L1 | A: "회의 시작합니다", "ㅇㅇ", "ㅋㅋ" | A 유효 메시지 == **1** | 리액션 제외 |
| TC-FR-3.3-02 | P0 | L1 | B: "(이모티콘)","(사진)","의견 정리했어요" | B == **1** | 미디어 태그 제외 |
| TC-FR-3.3-03 | P0 | L1 | C: "네","응","굳","구체적 피드백 드릴게요" | C == **1** | 1글자 응답 제외 |
| TC-FR-3.3-04 | P0 | L1 | 동일 입력 2회 호출 | 결과 완전 동일 | 결정론(NFR-1.3) |
| TC-FR-3.3-05 | P1 | L1 | 의미 있는 1문장만 | 그대로 1 카운트 | 정상 보존 |
| TC-FR-3.3-06 | P1 | L1 | StopwordFilter에 편집 API 부재 | `set_stopwords`/`add_stopword` 같은 공개 메서드 없음 | 편집 불가 |

```python
def test_stopword_excludes_reactions():                    # TC-FR-3.3-01
    recs = [MessengerRecord("A","t","회의 시작합니다"),
            MessengerRecord("A","t","ㅇㅇ"), MessengerRecord("A","t","ㅋㅋ")]
    assert StopwordFilter().count_valid_messages(recs)["A"] == 1

def test_stopword_deterministic():                         # TC-FR-3.3-04
    recs = [MessengerRecord("A","t","ㅋㅋ"), MessengerRecord("A","t","제안서 검토함")]
    f = StopwordFilter()
    assert f.count_valid_messages(recs) == f.count_valid_messages(recs)
```

---

# FR-4. 분석 — 정규화·이상 신호·가중치

## FR-4.1 Max 정규화

### 계약
```python
class Normalizer:                           # FR-4.1
    def normalize(self, values: list[float]) -> list[float]:
        """x / max. max==0 → 전원 0.0. round(_,4). 결과 0.0~1.0."""
```

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.1-01 | P0 | L1 | `[0,50,100]` | `[0.0, 0.5, 1.0]` | 기본 |
| TC-FR-4.1-02 | P0 | L1 | `[75,75,75]` | `[1.0,1.0,1.0]`, ZeroDivisionError 없음 | max==0 아님 |
| TC-FR-4.1-03 | P0 | L1 | 임의 양수 리스트 | 모든 v: `0.0<=v<=1.0` | 범위 |
| TC-FR-4.1-04 | P1 | L1 | `[1,2]` | `[0.5, 1.0]` | 2원소 |
| TC-FR-4.1-05 | P1 | L1 | `[10,20,30,40]` round 검증 | 각 값 소수점 4자리 | 반올림 |
| TC-FR-4.1-06 | P2 | L1 | `[]` (빈 입력) | `[]`(또는 계약상 정의된 안전값), 예외 없음 | 경계 |

```python
import pytest
@pytest.mark.parametrize("inp,exp",[
    ([0,50,100],[0.0,0.5,1.0]),                            # TC-FR-4.1-01
    ([75,75,75],[1.0,1.0,1.0]),                            # TC-FR-4.1-02
    ([0,0,0],[0.0,0.0,0.0]),                               # TC-FR-4.1-02 (zero max)
])
def test_normalize(inp, exp):
    assert Normalizer().normalize(inp) == exp
```

## FR-4.2 Capping + 로그 스케일 + 신호

### 계약
```python
class CappingScaler:                        # FR-4.2
    CAPPING_THRESHOLD: int = 50000
    def cap(self, additions: int) -> tuple[int, bool]:
        """additions>50000 → (50000, True). 그 외 (additions, False)."""
    def log_scale(self, total: int) -> float:   # math.log1p
```

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.2-01 | P0 | L1 | `cap(60000)` | `(50000, True)` | 상한 |
| TC-FR-4.2-02 | P0 | L1 | `cap(9999)` | `(9999, False)` | 미발동 |
| TC-FR-4.2-03 | P0 | L1 | `cap(50000)` | `(50000, False)` (경계: `>`만 cap) | 경계 |
| TC-FR-4.2-04 | P0 | L1 | `cap(50001)` | `(50000, True)` | 경계 직상 |
| TC-FR-4.2-05 | P1 | L1 | `log_scale(0)` | `0.0` (`log1p(0)`) | 로그 |
| TC-FR-4.2-06 | P0 | L1 | 60000줄 단일 커밋 포함 집계 | 내부 집계 기여분 50000으로 제한 + `capping_applied`/플래그 True | EW-01 |
| TC-FR-4.2-07 | P0 | L2 | Capping 발생 커밋 존재 | 신호 목록에 작성자·커밋 식별·변경량 포함 | 신호 표시 |
| TC-FR-4.2-08 | P0 | L1 | `detect_capping(repo)` — 12500줄 커밋 1 + 10줄 커밋 1 | 신호 1건, `{author, hash(7자), date, additions=12500}` | 커밋별 탐지 |
| TC-FR-4.2-09 | P1 | L1 | `detect_capping` — 50000줄 커밋(경계) | 신호 0건(`>`만) | 경계 |

## FR-4.2b 비정상 빈도 신호 (EW-02)

### 계약
```python
class AnomalySignalDetector:                # FR-4.2, FR-4.2b, FR-4.2d
    def detect_frequency(self, repo: dict[str, CommitStats]) -> list[dict]:
        """작성자 단기 커밋 빈도가 평소 일평균의 3배 초과 구간을 신호로.
           각 항목: {author, period, period_commits, baseline_avg}. (FR-4.2b)"""
    def detect_capping(self, repo: dict[str, CommitStats]) -> list[dict]:
        """단일 커밋 추가>50000인 커밋. 각 항목: {author, hash(7), date, additions}. (FR-4.2)"""
    def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
        """정규화 지표 Z-Score ≤ -1.5 가 2개 이상인 팀원명 리스트. (FR-4.2d)"""
    def build_signal_details(self, repo, scores) -> dict[str, list[dict]]:
        """팀원별 구조화 신호 상세(카드·예외용). signal_details 스키마로 통합."""
```

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.2b-01 | P0 | L1 | 평소 일 1커밋, 특정일 4커밋(>3배) | 해당 작성자·기간 신호 1건 | 빈도 폭주 |
| TC-FR-4.2b-02 | P0 | L1 | 신호 항목 필드 | author·기간·해당기간 커밋수·평소평균 모두 포함 | 항목 구성 |
| TC-FR-4.2b-03 | P1 | L1 | 균일 빈도(폭주 없음) | 신호 0건 | 오탐 방지 |

## FR-4.2c 이상 신호 예외 처리 (정상으로 표시)

신호 "정상으로 표시" 예외 상태(`NormalizedSignalsTracker`, L1)와 신호 카드 UI(`AnomalySignalPanel`, L3)를 검증한다. 신호는 점수 비반영(STR-7)이므로 예외 처리는 표시만 바꾸고 `total_score`를 변경하지 않는다.

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.2c-01 | P0 | L1 | `dismiss("A","CAPPING","h1")` 후 `is_dismissed` | True | 예외 등록 |
| TC-FR-4.2c-02 | P0 | L1 | `filter_details` — CAPPING h1 dismiss, h2 유지 | h2만 남음 | 근거 단위 필터 |
| TC-FR-4.2c-03 | P0 | L1 | 동일 유형 상세 전부 dismiss 후 `apply` | 해당 `signals` 라벨 제거 | 라벨 동기화 |
| TC-FR-4.2c-04 | P1 | L1 | 일부만 dismiss 후 `apply` | 라벨 유지(잔여 상세 존재) | 부분 유지 |
| TC-FR-4.2c-05 | P1 | L1 | `apply` 후 원본 scores | 원본 불변(replace 사본) | 불변성 |
| TC-FR-4.2c-06 | P0 | L3 | 카드 "정상으로 표시" 클릭 | `signal_dismissed(author,type,ref)` 발행(QSignalSpy) | UI 발행 |
| TC-FR-4.2c-07 | P1 | L3 | `signal_details` 없는 점수로 render | 카드 0개(빈 상태) | 빈 처리 |
| TC-FR-4.2c-08 | P1 | L3 | 유형별 상세 3종 render | CAPPING·EW-02·ZSCORE 카드 각 1개 | 유형 분류 |

```python
def test_apply_drops_label_when_all_details_dismissed():       # TC-FR-4.2c-03
    s = MemberScore("A",0.5,0.5,0.5,0.5,1,1,1,True,["CAPPING"],
                    [{"type":"CAPPING","hash":"h1","date":"d","additions":2000}])
    t = NormalizedSignalsTracker(); t.dismiss("A","CAPPING","h1")
    out = t.apply([s])
    assert out[0].signal_details == [] and "CAPPING" not in out[0].signals
```

## FR-4.2d Z-Score 하위 이상치 신호

> **번호 정합(확정):** 최종 체계는 `4.2(Capping)·4.2b(빈도)·4.2c(예외 처리)·4.2d(Z-Score)`이며 SRS 원체계·test-plan §1.3·RR v1.5와 일치한다. (구 RR 본문이 Z-Score를 `4.2c`로 오기했던 것을 v1.5에서 `4.2d`로 정정.)

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.2d-01 | P0 | L1 | 한 팀원 Git·문서 Z ≤ -1.5 (2개) | 그 팀원이 신호 리스트에 포함 | 2개 이상 조건 |
| TC-FR-4.2d-02 | P0 | L1 | Z ≤ -1.5 가 1개뿐 | 신호 아님 | 임계 미달 |
| TC-FR-4.2d-03 | P1 | L3 | 신호 팀원의 산점도 점 | ⚠ 오버레이 강조 | FR-5.1c 연동 |

```python
def test_zscore_two_low_axes():                            # TC-FR-4.2d-01
    scores = sample_scores(4)  # D팀원이 전 지표 하위
    flagged = AnomalySignalDetector().detect_zscore(scores)
    assert "D팀원" in flagged
```

## FR-4.3 데이터 소스 결측 → 동적 가중치 재조정

### 계약
```python
class WeightRebalancer:                      # FR-4.3
    def rebalance(self, weights: dict[str,float], available: set[str]) -> dict[str,float]:
        """결측 소스 가중치 0, 가용 소스는 상대 비율 유지 재정규화.
           반환 합 1.0±0.0001. 키 예: {'git','doc','msg'}."""
```

| TC-ID | P | L | 입력(균형 0.4/0.4/0.2) | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.3-01 | P0 | L1 | available={git,doc} (msg 결측) | git=0.5, doc=0.5, msg=0.0, 합 1.0±0.0001 | 메신저 결측 |
| TC-FR-4.3-02 | P0 | L1 | available={doc,msg} (git 결측) | 상대비 유지 재정규화, 합 1.0±0.0001 | Git 결측 |
| TC-FR-4.3-03 | P0 | L1 | available={git,msg} (doc 결측) | 합 1.0±0.0001 | 문서 결측 |
| TC-FR-4.3-04 | P0 | L1 | available={git} (1개만) | git=1.0, 나머지 0.0 | 단일 소스 |
| TC-FR-4.3-05 | P0 | L2 | 종합점수: 1개 소스만 가용 | total == 해당 소스 정규화 점수 | 단일 소스 점수 |
| TC-FR-4.3-06 | P0 | L1 | 동일 입력·조합 2회 | 결과 동일(결정론) | NFR-1.3 |
| TC-FR-4.3-07 | P0 | L2 | available=∅ (3개 전부 결측) | 분석 차단 + "분석 가능한 데이터 소스가 없습니다." | 전량 결측 |
| TC-FR-4.3-08 | P0 | L2 | 메신저 None vs 정상 | 종합점수 서로 다름 | 결측 영향 확인 |

```python
def test_rebalance_missing_msg():                          # TC-FR-4.3-01
    out = WeightRebalancer().rebalance(
        {"git":0.4,"doc":0.4,"msg":0.2}, available={"git","doc"})
    assert abs(out["git"]-0.5)<1e-4 and abs(out["doc"]-0.5)<1e-4
    assert out["msg"]==0.0 and abs(sum(out.values())-1.0)<1e-4

def test_single_source_full_weight():                      # TC-FR-4.3-04
    out = WeightRebalancer().rebalance(
        {"git":0.4,"doc":0.4,"msg":0.2}, available={"git"})
    assert abs(out["git"]-1.0)<1e-4 and out["doc"]==0.0 and out["msg"]==0.0
```

## FR-4.4 가중치 프리셋·슬라이더

### 계약
```python
class WeightPresetManager:                   # FR-4.4
    PRESETS = {"개발 중심":(0.60,0.25,0.15),
               "기획 중심":(0.20,0.60,0.20),
               "균형 설정":(0.40,0.40,0.20)}  # (git,doc,msg)
    def validate_sum(self, w_git, w_doc, w_msg) -> bool:  # 합 1.0 여부
    def normalize(self, weights) -> dict        # 합 1.0 비례 정규화
    def redistribute(self, key, new_value, current) -> dict  # 비례 재분배
    def match_preset(self, w_git, w_doc, w_msg) -> str | None  # 프리셋 역추적
```

**로직(L1):**

| TC-ID | P | L | 입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.4-01 | P0 | L1 | PRESETS["개발 중심"] | `(0.60,0.25,0.15)` | 프리셋 |
| TC-FR-4.4-02 | P0 | L1 | PRESETS["기획 중심"] | `(0.20,0.60,0.20)` | 프리셋 |
| TC-FR-4.4-03 | P0 | L1 | PRESETS["균형 설정"] | `(0.40,0.40,0.20)` | 프리셋 |
| TC-FR-4.4-04 | P0 | L1 | `validate_sum(0.5,0.5,0.5)` | False (합 1.5) | 합 검증 |
| TC-FR-4.4-05 | P0 | L1 | `validate_sum(0.4,0.4,0.2)` | True | 합 1.0 |
| TC-FR-4.4-10 | P0 | L1 | `redistribute("git",0.70,{git:.4,doc:.4,msg:.2})` | git=0.70, doc=0.20, msg=0.10, 합 1.0 | 비례 재분배 |
| TC-FR-4.4-11 | P1 | L1 | `redistribute("git",1.5,...)` | git 1.0으로 클램프, 합 1.0 | 클램프 |
| TC-FR-4.4-12 | P1 | L1 | `redistribute` 나머지 합 0 | 잔여 균등 분배 | 0 분모 방어 |
| TC-FR-4.4-13 | P1 | L1 | `normalize({git:2,doc:1,msg:1})` | git=0.5, 합 1.0 | 정규화 |
| TC-FR-4.4-14 | P1 | L1 | `match_preset(0.60,0.25,0.15)` / 커스텀값 | "개발 중심" / None | 역추적 |

**UI(L3):**

| TC-ID | P | L | 절차 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-4.4-06 | P0 | L3 | "개발 중심" 버튼 클릭 | 슬라이더 0.60/0.25/0.15 반영 | 프리셋 적용 |
| TC-FR-4.4-07 | P0 | L3 | 합 1.5로 슬라이더 설정 | [분석 시작] disabled + 경고 "가중치 합계가 1.00이어야 합니다. 현재: 1.50" | 비활성+경고 |
| TC-FR-4.4-08 | P0 | L3 | 합 1.0 | [분석 시작] enabled | 활성 |
| TC-FR-4.4-09 | P1 | L3 | 슬라이더 step | 0.05 단위로만 이동(범위 0.00~1.00) | step |
| TC-FR-4.4-15 | P0 | L3 | Git 슬라이더를 0.70으로 조작 | 나머지(문서·메신저) 슬라이더가 실시간으로 자동 연동되어 합 1.0 유지, 상대 비율 보존 | 실시간 연동 |
| TC-FR-4.4-16 | P0 | L3 | 슬라이더 조작 후 | 각 슬라이더 옆에 현재 가중치 값이 숫자(예: "0.70")로 표시됨 | 숫자 표시 |
| TC-FR-4.4-17 | P0 | L3 | 가중치 슬라이더 영역 상단 | "작업 종류 별 반영 비율" 설명 문구가 표시됨 | 헤더 문구 |
| TC-FR-4.4-18 | P1 | L3 | 슬라이더 3개 연속 조작 | 모든 조작 후 합 1.0±0.0001, 숫자 라벨이 슬라이더 값과 일치 | 연동 일관성 |

```python
def test_weight_slider_realtime_sync(qtbot):               # TC-FR-4.4-15
    ap = AnalysisPanel(); qtbot.addWidget(ap)
    ap.apply_preset("균형 설정")  # 0.40/0.40/0.20
    # Git 슬라이더를 0.70으로 변경
    ap.set_slider("git", 0.70)
    w = ap.current_weights()
    assert abs(w["git"] - 0.70) < 1e-2
    assert abs(sum(w.values()) - 1.0) < 1e-4   # 합 1.0 유지
    # 나머지가 상대 비율 보존: doc:msg = 2:1
    assert abs(w["doc"] / max(w["msg"], 1e-9) - 2.0) < 0.5

def test_weight_numeric_label(qtbot):                       # TC-FR-4.4-16
    ap = AnalysisPanel(); qtbot.addWidget(ap)
    ap.apply_preset("개발 중심")
    labels = ap.weight_label_texts()   # {"git":"0.60", "doc":"0.25", "msg":"0.15"}
    assert labels["git"] == "0.60" and labels["doc"] == "0.25" and labels["msg"] == "0.15"

def test_weight_area_header_label(qtbot):                   # TC-FR-4.4-17
    ap = AnalysisPanel(); qtbot.addWidget(ap)
    assert "작업 종류 별 반영 비율" in ap.header_text()
```

---

# FR-5. 시각화·리포트

## FR-5.1 차트 공통 규칙

| TC-ID | P | L | 절차 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-5.1-01 | P0 | L3 | 분석 미실행 상태 | 각 차트 패널에 **"분석할 데이터가 없습니다."** 안내 문구 표시 | placeholder |
| TC-FR-5.1-02 | P0 | L0 | 정적: 차트 위젯 상호 직접 참조 | 위젯 간 직접 import/참조 없음, Signal/Callback만 | 위젯 분리 |
| TC-FR-5.1-03 | P0 | L3 | 분석 완료 트리거 | 막대·레이더·산점도 **동시 갱신** | 동시 갱신 |

## FR-5.1a 막대 차트 — (FR-5.1d 자동검증과 연동)

| TC-ID | P | L | 검증 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-FR-5.1a-01 | P0 | L3 | 축 | X=팀원명, Y=종합지표, **Y범위 0.0~1.0 고정**, 그리드 0.2 |
| TC-FR-5.1a-02 | P0 | L3 | 색상 | 1위 강조색 + 나머지 기본색 |
| TC-FR-5.1a-03 | P0 | L3 | hover 툴팁 6항목 | 팀원명 / Git 정규화 점수(**및 원시 추가 라인 수 등 구성요소**) / 문서 정규화 점수(**및 원시 글자수 등 구성요소**) / 메신저 정규화 점수(**및 원시 유효 발화수 등 구성요소**) / 종합 기여 지표 / Capping 발동 여부 |
| TC-FR-5.1a-04 | P1 | L3 | 툴팁 위치 | 우측상단 오프셋, 경계 시 좌측 반전 |
| TC-FR-5.1a-05 | P0 | L3 | 팀 평균선 | 수평 점선 + "팀 평균: X.XX", Y=산술평균±0.0001 |
| TC-FR-5.1a-06 | P0 | L3 | 막대 상단 라벨 | 소수점 2자리 수치 |
| TC-FR-5.1a-07 | P0 | L3 | 애니메이션 | 하단→최종, 20프레임·30ms |
| TC-FR-5.1a-08 | P0 | L3 | 애니 종료 후 높이 | 종합지표 ±0.001 |
| TC-FR-5.1a-09 | P1 | L3 | 애니 중 hover | 비활성, 완료 후 활성 |
| TC-FR-5.1a-10 | P0 | L3 | 툴팁 원시값 | 툴팁에 Git 원시 추가 라인 수, 문서 원시 글자수, 메신저 원시 발화 수가 각각 숫자로 표시됨 |

> **v1.3 변경(점수 구성요소 노출).** RR v1.6에 따라 막대 차트 툴팁의 6항목에 각 점수의 정량적 세부 구성요소(Raw Data)가 포함된다. Git 정규화 점수 옆에 원시 추가 라인 수, 문서 정규화 점수 옆에 원시 글자수, 메신저 정규화 점수 옆에 원시 유효 발화 수가 함께 표시되어야 한다.

## FR-5.1b 레이더 차트

| TC-ID | P | L | 검증 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-FR-5.1b-01 | P0 | L3 | 축 레이블 | "Git"/"문서"/"메신저" 정확 |
| TC-FR-5.1b-02 | P0 | L3 | 그리드 | 0.2 간격 5단계 |
| TC-FR-5.1b-03 | P0 | L3 | 폴리곤 수 | 팀원 N + 팀평균 = **N+1** |
| TC-FR-5.1b-04 | P0 | L3 | 팀평균 폴리곤 | 회색 점선, 범례 "팀 평균" |
| TC-FR-5.1b-05 | P0 | L3 | 범례 토글 | 클릭 시 해당 폴리곤 show/hide |
| TC-FR-5.1b-06 | P1 | L3 | 토글 상태 | bool 리스트 관리, 재분석 시 초기화 |
| TC-FR-5.1b-07 | P0 | L3 | 꼭짓점 hover 4항목 | 팀원명/지표명/정규화점수/원시값 |
| TC-FR-5.1b-08 | P0 | L3 | 결측 축 | 점선 + "(제외됨)" 레이블 |
| TC-FR-5.1b-09 | P0 | L3 | 애니 종료 후 반경 | 정규화점수 ±0.001, 50ms 순차 딜레이 |

## FR-5.1c 산점도

| TC-ID | P | L | 검증 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-FR-5.1c-01 | P0 | L3 | 축 | 가용 데이터 수에 따라 동적 매핑(1개: 안내문구, 2~3개: 축 매핑) |
| TC-FR-5.1c-02 | P0 | L3 | 3개 데이터 매핑 | 점 색상(채도)가 세 번째 데이터에 비례 |
| TC-FR-5.1c-03 | P0 | L3 | 1개 데이터 결측(총 2개) | Y축 첫 번째/X축 두 번째, 색상 고정 |
| TC-FR-5.1c-04 | P0 | L3 | 2개 데이터 결측(총 1개) | 차트 대신 "자료가 한 종류인 경우..." 텍스트 표시 |
| TC-FR-5.1c-05 | P0 | L3 | 십자선 | X=동적평균±0.0001, Y=동적평균±0.0001, "팀 평균" 마커 |
| TC-FR-5.1c-06 | P0 | L3 | 라벨 겹침 | 최소거리 ≥30px, 4방향 자동 조정 |
| TC-FR-5.1c-07 | P0 | L3 | 동적 hover 툴팁 | 가용 소스 정규화/원시지표 동적 노출 |
| TC-FR-5.1c-08 | P0 | L3 | 점 클릭 | `scatter_member_selected(str)` 발행 → 레이더 폴리곤 굵기 2배 1.5초 |
| TC-FR-5.1c-09 | P0 | L3 | 하위이상치 점 | 경고 ⚠ 오버레이 |
| TC-FR-5.1c-10 | P1 | L3 | fade-in 애니 | 점 알파 및 색상 0→최종 동시 |

## FR-5.1d 차트 자동 검증 — **12개 pytest 케이스 (G4 게이트)**

이 12개가 전부 통과해야 한다. **TC-ID = 함수명**으로 1:1 고정.

| # | 함수명(테스트) | 검증 |
| :-- | :-- | :-- |
| 1 | `test_bar_tooltip_items` | 막대 hover 툴팁 6항목 존재 |
| 2 | `test_bar_average_line` | 평균선 Y == 산술평균 ±0.0001 |
| 3 | `test_bar_animation_final_height` | 애니 완료 후 높이 == 종합지표 ±0.001 |
| 4 | `test_radar_vertex_labels` | 꼭짓점 "Git"/"문서"/"메신저" 정확 |
| 5 | `test_radar_toggle_hide` | 범례 토글 후 폴리곤 visible=False |
| 6 | `test_radar_missing_data` | 결측 시 "(제외됨)" 레이블 존재 |
| 7 | `test_scatter_dynamic_axes` | 데이터 개수에 따른 축/텍스트 표시 |
| 8 | `test_scatter_dot_color_saturation` | 3개 소스일 때 그라데이션 보간 범위 검증 |
| 9 | `test_scatter_signal_emission` | 클릭 시 Signal 발행(QSignalSpy) |
| 10 | `test_scatter_label_overlap` | 라벨 최소거리 ≥30px |
| 11 | `test_scatter_dynamic_crosshair` | 십자선 X/Y == 동적 축 평균 ±0.0001 |
| 12 | `test_scatter_placeholder_text` | 1개 소스일 때 안내 텍스트 유무 검증 |

```python
# tests/ui/test_chart_acceptance.py
def test_bar_average_line(qtbot):                          # FR-5.1d #2
    w = BarChartWidget(); qtbot.addWidget(w)
    scores = sample_scores(4)
    w.render(scores)
    expected = sum(s.total_score for s in scores)/len(scores)
    assert abs(w.average_line_y() - expected) < 1e-4

def test_scatter_signal_emission(qtbot):                   # FR-5.1d #9
    w = ScatterChartWidget(); qtbot.addWidget(w)
    w.render(sample_scores(4))
    with qtbot.waitSignal(w.member_selected, timeout=1000) as blocker:
        w.simulate_point_click(index=0)
    assert isinstance(blocker.args[0], str)

def test_bar_animation_final_height(qtbot):                # FR-5.1d #3
    w = BarChartWidget(); qtbot.addWidget(w)
    scores = sample_scores(4); w.render(scores)
    qtbot.waitUntil(lambda: w.animation_done, timeout=3000)
    for s in scores:
        assert abs(w.bar_height(s.author) - s.total_score) < 1e-3
```

> 위젯은 테스트 가능한 접근자(`average_line_y()`, `bar_height(name)`, `vertex_labels()`, `dot_size(name)`, `quadrant_labels()`, `crosshair()`, `animation_done`, `simulate_point_click()`)를 노출해야 한다. 이는 렌더 픽셀 비교를 피하고 데이터 계약을 검증하기 위함이다.

## FR-5.2 리포트 저장 (.md/.csv)

### 계약
```python
class ReportExporter:                        # FR-5.2, FR-5.3
    def to_markdown(self, scores: list[MemberScore], missing: set[str]) -> str
    def to_csv(self, scores: list[MemberScore], missing: set[str]) -> bytes  # utf-8-sig
```

| TC-ID | P | L | 검증 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-FR-5.2-01 | P0 | L1 | .md 출력 | 마크다운 테이블 구조(헤더+행) 정상 |
| TC-FR-5.2-02 | P0 | L1 | .csv 바이트 | **BOM `\xef\xbb\xbf`** 로 시작(Excel 한글) |
| TC-FR-5.2-03 | P0 | L1 | 한글 author CSV | 디코딩 시 무손상 |
| TC-FR-5.2-04 | P0 | L1 | 헤더 표현 | "종합 지표"(동의어) 사용, "최종 평가" 등 판정 뉘앙스 금지 | STR-7/P5 |
| TC-FR-5.2-05 | P1 | L3 | 저장 성공 | 상태바 경로 메시지 3초 표시 후 사라짐 |

```python
def test_csv_has_bom():                                    # TC-FR-5.2-02
    data = ReportExporter().to_csv(sample_scores(2), missing=set())
    assert data[:3] == b"\xef\xbb\xbf"

def test_no_verdict_wording():                             # TC-FR-5.2-04
    md = ReportExporter().to_markdown(sample_scores(2), missing=set())
    assert "최종 평가" not in md and ("종합 지표" in md or "종합" in md)
```

## FR-5.3 데이터 소스 결측 경고

문구 형식: `⚠ [데이터 소스명] 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다.` (`[데이터 소스명]`∈{Git,문서,메신저}).

| TC-ID | P | L | 입력 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-FR-5.3-01 | P0 | L3 | 메신저 결측 | UI 노란 배경 배너 + 위 문구("메신저") |
| TC-FR-5.3-02 | P0 | L1 | md(missing={"메신저"}) | 하단 블록쿼트(`>`)로 동일 문구 |
| TC-FR-5.3-03 | P0 | L1 | csv(missing={"메신저"}) | 빈 행 후 "WARNING" 행 + 동일 문구 |
| TC-FR-5.3-04 | P0 | L1 | missing 복수 {"Git","메신저"} | 결측 소스 각각 배너/경고 |
| TC-FR-5.3-05 | P0 | L1 | missing=∅ | 배너·경고 미포함 |
| TC-FR-5.3-06 | P1 | L3 | 산점도/레이더 | 결측 상황에 따른 동적 시각 표시(FR-5.1b/c 참조) |

## FR-5.4 3-스크린 네비게이션

화면 전환은 Controller 슬롯(`show_submit`/`show_loading`/`show_result`) 호출로 일어난다. View는 `QStackedWidget` 현재 페이지로 검증한다.

| TC-ID | P | L | 절차 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-5.4-01 | P0 | L3 | 앱 기동(캐시 없음) | 현재 화면 == 제출(SubmitScreen) | 기동 화면 |
| TC-FR-5.4-02 | P0 | L3 | `show_loading()` 호출 | 현재 화면 == 로딩(LoadingScreen) | 분석 진입 |
| TC-FR-5.4-03 | P0 | L3 | `show_result()` 호출 | 현재 화면 == 결과(ResultScreen) | 완료 전환 |
| TC-FR-5.4-04 | P1 | L3 | 로딩 중 오류 → `show_submit()` | 현재 화면 == 제출 | 오류 복귀 |
| TC-FR-5.4-05 | P0 | L3 | 결과 화면 [새 분석] → `new_analysis_requested` | Signal 발행, 제출 화면 복귀 | 새 분석 |
| TC-FR-5.4-06 | P1 | L3 | 캐시 단독 로드 후 기동 | 즉시 결과 화면 표시(NFR-2.4) | 캐시 진입 |
| TC-FR-5.4-07 | P0 | L2 | [새 분석] 후 제출 화면 복귀 | 이전에 입력한 문서 파일, 메신저 파일, 깃 저장소 경로 및 화면 표시 상태가 **모두 초기화**됨 | 입력 초기화 |
| TC-FR-5.4-08 | P0 | L3 | [새 분석] 후 제출 화면의 입력 표시 | 문서·메신저·깃 입력 표시가 "없음"으로 복귀, 적재 피드백 초기화 | 표시 초기화 |

```python
def test_new_analysis_resets_inputs(qtbot):                 # TC-FR-5.4-07
    mw = MainWindow(); qtbot.addWidget(mw)
    # 파일 적재 시뮬레이션
    mw.submit._doc_paths = ["a.docx", "b.pptx"]
    mw.submit._msg_path = "chat.txt"
    mw.submit._git_repo = "C:/repo"
    # 새 분석 실행
    mw.show_submit()  # new_analysis_requested → show_submit
    mw.submit.clear_inputs()
    assert mw.submit._doc_paths == []
    assert mw.submit._msg_path is None
    assert mw.submit._git_repo is None

def test_new_analysis_resets_display(qtbot):                # TC-FR-5.4-08
    ss = SubmitScreen(); qtbot.addWidget(ss)
    ss._doc_paths = ["a.docx"]; ss._msg_path = "chat.txt"; ss._git_repo = "repo"
    ss.clear_inputs()
    assert "없음" in ss.git_display_text()
    assert "없음" in ss.doc_display_text()
    assert "없음" in ss.msg_display_text()
```

## FR-5.5 메인(제출) 화면

| TC-ID | P | L | 절차/입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-5.5-01 | P1 | L3 | 제출 화면 표시 | 로고 위젯 존재 + 설명 텍스트(1줄 이상) | 로고·설명 |
| TC-FR-5.5-02 | P0 | L3 | `_handle_dropped_paths(["a.docx","b.pptx","c.hwpx"])` | `documents_dropped`==`["a.docx","b.pptx","c.hwpx"]` | 문서 드롭 |
| TC-FR-5.5-03 | P0 | L3 | `_handle_dropped_paths(["chat.txt"])` | `messenger_dropped`=="chat.txt" | 카톡 드롭 |
| TC-FR-5.5-04 | P1 | L3 | 문서 3개 적재 | 적재 피드백 문자열에 "3" 포함 | 적재 피드백 |
| TC-FR-5.5-05 | P0 | L3 | AnalysisPanel 합계 ≠ 1.0 | [분석 시작] disabled (FR-4.4 슬롯) | 가중치 검증 |
| TC-FR-5.5-06 | P0 | L3 | Git 저장소 선택 후 | 선택된 Git 저장소 이름이 화면에 표시됨 | 깃 저장소 표시 |
| TC-FR-5.5-07 | P0 | L3 | 문서 파일 적재 후 | 입력된 문서 파일명이 화면에 표시됨 | 문서 파일명 표시 |
| TC-FR-5.5-08 | P0 | L3 | 메신저 파일 적재 후 | 입력된 메신저 파일명이 화면에 표시됨 | 메신저 파일명 표시 |
| TC-FR-5.5-09 | P0 | L3 | 입력 없는 상태 | Git 저장소·문서·메신저 각각 "없음"으로 표시됨 | 미입력 표시 |

```python
def test_submit_shows_git_repo_name(qtbot):                # TC-FR-5.5-06
    ss = SubmitScreen(); qtbot.addWidget(ss)
    ss.set_git_repo("C:/Users/test/my-project")
    assert "my-project" in ss.git_display_text()

def test_submit_shows_no_input(qtbot):                     # TC-FR-5.5-09
    ss = SubmitScreen(); qtbot.addWidget(ss)
    assert "없음" in ss.git_display_text()
    assert "없음" in ss.doc_display_text()
    assert "없음" in ss.msg_display_text()
```

## FR-5.6 분석 로딩 화면

| TC-ID | P | L | 절차 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-5.6-01 | P0 | L3 | `LoadingScreen.start()` | 진행률 표시(visible), 값 0 | 출현 |
| TC-FR-5.6-02 | P0 | L3 | `set_value(60)` | 진행률 값 60 | 갱신 |
| TC-FR-5.6-03 | P0 | L3 | `finish()` | 진행률 숨김 | 종료 |

## FR-5.7 결과 화면 계정 병합 (post-hoc N:1)

### 계약 (재집계 경로)
```python
# View(ResultScreen)는 merge_requested(mapping)만 발행한다.
# 재집계는 Controller가 보유한 원시 지표에 mapping을 적용해 수행:
#   AliasMapper.merge(raw, mapping) → ContributionAggregator.aggregate(...) (재정규화)
# 정규화는 팀원 집합 전체 의존 → 병합 시 모든 팀원 점수가 갱신될 수 있다(FR-4.1).
```

| TC-ID | P | L | 절차/입력 | 기대 | 근거 |
| :-- | :- | :- | :-- | :-- | :-- |
| TC-FR-5.7-01 | P0 | L3 | `ResultScreen.render(scores, missing)` | 결과의 모든 author가 병합 후보에 제시 | 후보 제시 |
| TC-FR-5.7-02 | P0 | L3 | 복수 인물 선택 후 병합 확정 | `merge_requested({alias→member})` 발행(QSignalSpy) | 병합 발행 |
| TC-FR-5.7-03 | P0 | L2 | `AliasMapper.merge` 후 `aggregate` 재호출 | 병합 인물 원시 지표 합산 + 전체 재정규화로 타 팀원 점수도 갱신 | 재집계 |
| TC-FR-5.7-04 | P1 | L2 | 병합 해제(분리) 매핑으로 재집계 | 분리 전 상태와 동일 결과 | 병합 취소 |
| TC-FR-5.7-05 | P0 | L2 | 동일 병합 입력 2회 재집계 | 결과 완전 일치(NFR-1.3) | 결정론 |
| TC-FR-5.7-06 | P1 | L2 | 재집계 진행 중 추가 병합 요청 | `is_analyzing` 가드로 차단(NFR-1.2) | 중복 차단 |
| TC-FR-5.7-07 | P0 | L3 | 매핑 대상을 **하나도 선택하지 않은** 상태에서 OK 클릭 | OK 버튼이 비활성(disabled)이어서 눌리지 않음. 빈 화면 출력 방지 | 빈 매핑 차단 |
| TC-FR-5.7-08 | P0 | L3 | 매핑 기능에서 **Cancel(취소)** 버튼 클릭 | 매핑만 취소되고 매핑 기능 자체는 사라지지 않음. 기존 차트·결과 화면 상태 유지 | Cancel 안전 처리 |
| TC-FR-5.7-09 | P0 | L3 | 매핑 1건 이상 선택 후 | OK 버튼이 활성(enabled)으로 전환 | OK 활성 조건 |
| TC-FR-5.7-10 | P1 | L3 | Cancel 후 다시 매핑 시도 | 매핑 컨트롤이 정상적으로 사용 가능(이전 Cancel로 파괴되지 않음) | Cancel 후 재사용 |

```python
def test_result_merge_emits_signal(qtbot):                 # TC-FR-5.7-02
    rs = ResultScreen(); qtbot.addWidget(rs)
    rs.render(sample_score_dicts(4), set())
    # 병합 컨트롤에서 두 인물을 같은 팀원으로 지정
    rs.merge.combo_for("이대한").setCurrentText("이대한")
    rs.merge.combo_for("daehan.lee").setCurrentText("이대한")
    with qtbot.waitSignal(rs.merge_requested, timeout=1000) as blocker:
        rs.merge._confirm()
    assert blocker.args[0]["daehan.lee"] == "이대한"

def test_merge_reaggregation_changes_others(...):          # TC-FR-5.7-03 (L2, Controller+Model)
    # 두 계정 병합 → 재정규화로 나머지 팀원 정규화 점수가 병합 전과 달라짐을 검증
    ...

def test_empty_mapping_ok_disabled(qtbot):                  # TC-FR-5.7-07
    rs = ResultScreen(); qtbot.addWidget(rs)
    rs.render(sample_score_dicts(4), set())
    # 아무것도 선택하지 않은 상태
    assert not rs.merge.ok_button.isEnabled(), "매핑 0건에서 OK 버튼이 활성화되면 안 됨"

def test_cancel_preserves_state(qtbot):                     # TC-FR-5.7-08
    rs = ResultScreen(); qtbot.addWidget(rs)
    rs.render(sample_score_dicts(4), set())
    chart_data_before = rs.dashboard.bar.bar_heights()
    rs.merge._cancel()  # Cancel 클릭
    # 매핑 기능이 사라지지 않아야 함
    assert rs.merge.isVisible() or rs.merge_button.isEnabled()
    # 차트 상태가 유지되어야 함
    assert rs.dashboard.bar.bar_heights() == chart_data_before

def test_mapping_one_selection_enables_ok(qtbot):           # TC-FR-5.7-09
    rs = ResultScreen(); qtbot.addWidget(rs)
    rs.render(sample_score_dicts(4), set())
    assert not rs.merge.ok_button.isEnabled()
    # 1건 이상 매핑
    rs.merge.combo_for("daehan.lee").setCurrentText("이대한")
    assert rs.merge.ok_button.isEnabled()
```

> **레이어 책임.** TC-FR-5.7-01·02·07~10은 View(L3, 이대한). TC-FR-5.7-03~06은 재집계 경로로 Controller+Model(L2)이며, AliasMapper·ContributionAggregator·AnalysisOrchestrator의 병합 재호출 지원에 의존한다(controller-design.md 담당자 협의 대상).

---

# NFR-1. UI 응답성·동시성

## NFR-1.1 비동기 분석 (pytest-qt)

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-1.1-01 | P0 | L3 | 대용량(5,000줄) 분석 중 메인윈도우 이벤트 처리 | UI 프리징 없음(이벤트 응답) |
| TC-NFR-1.1-02 | P0 | L3 | 분석 시작 | 1초 이내 진행률 표시 출현 |
| TC-NFR-1.1-03 | P0 | L3 | 완료/오류 | 진행률 사라짐 + 결과/오류 메시지 |
| TC-NFR-1.1-04 | P1 | L3 | 차트 애니 재생 중 | 메인윈도우 응답성 유지 |

## NFR-1.2 중복 실행 방지

### 계약 (AnalysisOrchestrator, architecture §5.4)
```python
class AnalysisOrchestrator(QObject):
    progress=pyqtSignal(int); completed=pyqtSignal(list); failed=pyqtSignal(str)
    is_analyzing: bool = False
    def start_analysis(self, config: dict) -> None:
        """is_analyzing True면 즉시 return. 아니면 True 잠금 후 Worker 기동."""
    def _on_worker_finished(self) -> None:
        """성공·오류·취소 무관 is_analyzing=False + 버튼 재활성 Signal."""
```

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-1.2-01 | P0 | L2 | start 직후 | 0.5초 이내 버튼 disabled |
| TC-NFR-1.2-02 | P0 | L2 | start 5회 연속 호출 | Worker 1개만 (활성 스레드 수 검증) |
| TC-NFR-1.2-03 | P0 | L2 | 완료 후 재분석 | 결과 첫 실행과 동일(중복 누적 없음) |
| TC-NFR-1.2-04 | P0 | L2 | Worker가 RuntimeError | `is_analyzing=False` 복원 + 버튼 재활성 |
| TC-NFR-1.2-05 | P0 | L2 | 모든 종료 경로(성공/오류/취소) | 상태 복원 보장 |

```python
def test_guard_blocks_duplicates(qtbot, monkeypatch):      # TC-NFR-1.2-02
    orch = AnalysisOrchestrator()
    started = []
    monkeypatch.setattr(orch, "_spawn_worker", lambda cfg: started.append(1))
    for _ in range(5):
        orch.start_analysis({"dummy": True})
    assert sum(started) == 1 and orch.is_analyzing is True

def test_state_restored_on_error(qtbot):                   # TC-NFR-1.2-04
    orch = AnalysisOrchestrator()
    orch.is_analyzing = True
    orch._on_worker_finished()    # 오류 경로 모사
    assert orch.is_analyzing is False
```

## NFR-1.3 분석 결정론

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-1.3-01 | P0 | L1 | 동일 입력·가중치 2회 aggregate | 두 결과 완전 일치 |
| TC-NFR-1.3-02 | P0 | L1 | 동일 입력 불용어 분류 2회 | 동일 |

---

# NFR-2. 보안·프라이버시

## NFR-2.1 읽기 전용 입력

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-2.1-01 | P0 | L1 | 분석 전후 원본 `getmtime` | 동일(수정 안 됨) |
| TC-NFR-2.1-02 | P0 | L0 | 정적: 분석 모듈의 쓰기 호출 | 분석 대상 경로에 `'w'/'a'/'x'`·move·remove 0건(화이트리스트 제외) |

```python
def test_input_not_modified(tmp_docx):                     # TC-NFR-2.1-01
    import os
    p = tmp_docx("A", "x"*100); before = os.path.getmtime(p)
    DocumentParser().parse(p)
    assert os.path.getmtime(p) == before
```

## NFR-2.2 네트워크 차단

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-2.2-01 | P0 | L0 | 정적 import 스캔 | requests/urllib/httpx/socket/http.client 0건 |
| TC-NFR-2.2-02 | P0 | L1 | conftest `_no_network` 활성 하 전 테스트 | 네트워크 connect 시도 0건(시도 시 RuntimeError) |
| TC-NFR-2.2-03 | P1 | L3 | 외부 링크 | `webbrowser.open`만 사용(앱 내부 HTTP 없음) |

## NFR-2.3 캐시 무결성·민감정보 비저장

### 계약 (CacheManager)
```python
class CacheManager:                          # NFR-2.3, NFR-2.4
    def save(self, data: dict) -> None:      # tmp 쓰기→fsync→os.replace, json만
    def load(self) -> dict:                  # JSONDecodeError/KeyError → 삭제+빈 dict
```

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-2.3-01 | P0 | L1 | save 후 load | json.loads로 점수 dict 정상 복원 |
| TC-NFR-2.3-02 | P0 | L1 | 저장 데이터에 메시지 본문 포함 시도 | 캐시에 본문 미포함(저장 화이트리스트 검증) → 포함 시 Fail |
| TC-NFR-2.3-03 | P0 | L0 | 정적: `import pickle`/`from pickle` | 0건 |
| TC-NFR-2.3-04 | P0 | L1 | 손상 캐시(깨진 JSON) load | 파일 삭제 + 빈 상태 반환, 예외 없음 |
| TC-NFR-2.3-05 | P0 | L1 | save 직후 | `.qce_cache.tmp` 디스크 잔존 없음 |
| TC-NFR-2.3-06 | P1 | L1 | save 중 강제 종료 모사 후 재시작 load | 손상 안내 다이얼로그 + 초기화면 |

```python
def test_atomic_no_tmp_left(tmp_path, monkeypatch):        # TC-NFR-2.3-05
    monkeypatch.chdir(tmp_path)
    CacheManager().save({"scores":{"A":0.3},"ts":"2026-01-01T00:00"})
    import os
    assert not os.path.exists(".qce_cache.tmp")
    assert os.path.exists(".qce_cache")

def test_corrupt_cache_recovers(tmp_path, monkeypatch):    # TC-NFR-2.3-04
    monkeypatch.chdir(tmp_path)
    open(".qce_cache","w").write("{not json")
    out = CacheManager().load()   # must not raise
    import os
    assert out == {} and not os.path.exists(".qce_cache")
```

## NFR-2.4 캐시 단독 로드

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-2.4-01 | P0 | L1/L3 | 원본 전체 삭제 후 캐시만으로 시작 | 차트·점수 정상 표시 |
| TC-NFR-2.4-02 | P1 | L3 | 캐시 로드 시 | 상태바 "캐시 파일에서 이전 분석 결과를 불러왔습니다. (분석 일시: YYYY-MM-DD HH:MM)" |

---

# NFR-3. 안정성

## NFR-3.1 인코딩 자동 감지

### 계약
```python
class EncodingHandler:                        # NFR-3.1
    def read_text(self, path: str) -> str | dict[str,str]:
        """UTF-8 → CP949 순. 둘 다 실패 → {"error":"encoding_failed","path":path}."""
```

| TC-ID | P | L | 입력 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-3.1-01 | P0 | L1 | UTF-8 한글 파일 | str 반환, 1회 시도 성공, 무손상 |
| TC-NFR-3.1-02 | P0 | L1 | CP949 한글 파일 | 한글 무손상 |
| TC-NFR-3.1-03 | P0 | L1 | Shift-JIS(미지원) 파일 | 종료 없이 `{"error":"encoding_failed","path":...}` |
| TC-NFR-3.1-04 | P1 | L1 | 미지원 후 앱 계속 | 후속 호출 정상(프로세스 생존) |

```python
def test_encoding_cp949(tmp_path):                         # TC-NFR-3.1-02
    p = tmp_path/"c.txt"; p.write_bytes("한글테스트".encode("cp949"))
    assert EncodingHandler().read_text(str(p)) == "한글테스트"

def test_encoding_unsupported(tmp_path):                   # TC-NFR-3.1-03
    p = tmp_path/"s.txt"; p.write_bytes("テスト".encode("shift_jis"))
    out = EncodingHandler().read_text(str(p))
    assert isinstance(out, dict) and out["error"] == "encoding_failed"
```

## NFR-3.2 데이터 모듈 상호 격리

| TC-ID | P | L | 절차 | 기대 |
| :-- | :- | :- | :-- | :-- |
| TC-NFR-3.2-01 | P0 | L0 | 정적: 파서 3종 상호 import | 0건(test-plan §7.4) |
| TC-NFR-3.2-02 | P0 | L2 | messenger_parser 모듈 제거/rename 후 git·document 단위테스트 | ImportError 없이 통과(3 조합) |
| TC-NFR-3.2-03 | P0 | L2 | 1개 모듈 RuntimeError Mock | 나머지 2개 결과가 최종 결과에 포함(3 조합) |
| TC-NFR-3.2-04 | P0 | L2 | 1개 소스만 가용 | 분석 정상 종료 + FR-4.3 재조정 적용 |
| TC-NFR-3.2-05 | P0 | L2 | 전체 통합 pytest | 종료코드 0 |

```python
def test_isolation_one_module_fails(monkeypatch):          # TC-NFR-3.2-03
    # GitAnalyzer.analyze가 터져도 문서·메신저 결과는 살아 있어야 한다.
    monkeypatch.setattr(GitAnalyzer, "analyze",
        lambda self, p: (_ for _ in ()).throw(RuntimeError("git down")))
    result = ContributionAggregator().aggregate(
        git=None, docs={"A":100}, msgs={"A":5},
        weights={"git":0.4,"doc":0.4,"msg":0.2})
    assert any(m.author == "A" for m in result)   # 문서·메신저 기여 반영됨
```

---

# 부록 A. 수동 시스템 테스트 체크리스트 (L4 — `system/manual_checklist.md`)

### 시나리오 A — 학기말 종합 평가 (메인)
- [ ] A-01 `QCE.exe` 더블클릭 → 메인 윈도우(팀원 패널/드롭영역/신호영역) 표시, **전용 아이콘 적용 확인(NFR-4.1)**
- [ ] A-02 .pptx/.docx/.hwpx 8개 Drag&Drop → "8/8 적재 완료", **입력된 문서 파일명 표시 확인**
- [ ] A-03 Git 저장소 선택 → 커밋 수집(500커밋 ≤60s 체감), **선택된 저장소 이름 표시 확인**
- [ ] A-04 카톡 .txt 적재 → 자동 불용어 적용, 사용자 편집 UI **없음** 확인, **입력된 메신저 파일명 표시 확인**
- [ ] A-04a **카톡만 단독 입력** 후 [분석 시작] → 앱이 멈추지 않고 분석 결과 화면 정상 표시
- [ ] A-05 결과 화면 매핑 컨트롤에 전 소스 식별자 노출(**카톡 발화자 포함**) → N:1 매핑
- [ ] A-05a 매핑 **0건** 상태에서 OK 버튼 **비활성** 확인
- [ ] A-05b 매핑 기능에서 **Cancel** 클릭 → 매핑만 취소되고 **기존 차트·결과 화면 유지** 확인
- [ ] A-06 [분석 시작] → 진행률 표시 → 완료
- [ ] A-06a **가중치 슬라이더** 조작 시 나머지 슬라이더가 **실시간 자동 연동**, 현재 가중치 **숫자 표시** 확인
- [ ] A-06b 가중치 슬라이더 영역 상단에 **"작업 종류 별 반영 비율"** 문구 표시 확인
- [ ] A-07 막대/레이더/산점도 3종 동시 표시 + 인터랙션(툴팁에 **원시값 구성요소 포함**/토글/클릭연동)
- [ ] A-07a 분석 미실행 상태에서 차트 패널에 **"분석할 데이터가 없습니다."** 표시 확인
- [ ] A-08 신호 영역에 EW-01/EW-02/Z-Score 신호 표시
- [ ] A-09 [새 분석] 클릭 → 제출 화면 복귀, **이전 입력 데이터(문서·메신저·깃) 모두 초기화** 확인
- [ ] A-09a 입력 없는 상태에서 Git·문서·메신저 각각 **"없음"** 표시 확인

### 시나리오 B — 어뷰징 의심 대응
- [ ] B-01 EW-01 신호 카드 클릭 → 커밋 해시/작성일/파일 목록 표시
- [ ] B-02 신호가 종합 점수에 **자동 반영되지 않음** 확인(판정 금지 P5)
- [ ] B-03 리포트 export → 신호 유지된 채 저장

### 시나리오 C — 신원 매핑 갱신
- [ ] C-01 새 GitHub 계정 alias 추가 등장 → 기존 팀원에 N:1 매핑
- [ ] C-02 매핑 후 막대/산점도에서 단일 인격으로 합산 확인

### 시나리오 D — 실행 파일 아이콘 (NFR-4.1)
- [ ] D-01 빌드된 `QCE.exe` 파일에 **QCE 전용 아이콘(.ico)**이 적용되어 표시됨

---

# 부록 B. 미커버 점검 (G8)

아래 FR/NFR 중 `test-cases.md`에 케이스가 **하나도 없으면** G8 위반 → 즉시 추가.
`FR-1.1 1.2 1.3 / 2.1 2.2 / 3.1 3.2 3.3 / 4.1 4.2 4.2b 4.2c 4.2d 4.3 4.4 / 5.1 5.1a 5.1b 5.1c 5.1d 5.2 5.3 5.4 5.5 5.6 5.7`
`NFR-1.1 1.2 1.3 / 2.1 2.2 2.3 2.4 / 3.1 3.2 / 4.1`
(본 문서 기준 전 항목 커버됨 — 확장 시 본 목록과 §10 추적표를 동기화한다.)

---

# 부록 C. 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
|v1.0|2026-05-29|최초 작성. 전 FR/NFR에 대한 실행 가능 케이스, 계약 블록, pytest 스켈레톤, 12개 차트 게이트, 수동 체크리스트, 미커버 점검 포함. RR v1.3 기준(슬랙 제외·3종 차트·FR-4.2d 통일).| 이대한 |
| **v1.1** | **2026-05-31** | **RR v1.4·view-design v1.3 동기화: FR-5.4(3-스크린 네비게이션)·FR-5.5(제출 화면)·FR-5.6(로딩 화면)·FR-5.7(결과 화면 계정 병합 재집계) 케이스 신설. FR-5.7은 View(L3) + 재집계 경로(Controller+Model, L2)로 분리. 부록 B 미커버 점검 목록에 5.4~5.7 추가.** | QCE 개발팀 (이대한) |
|**v1.2**|**2026-05-31**|**구 SRS.md 폐지 반영(A1~A4). (1) **FR-4.2c 이상 신호 예외 처리 섹션 신설**(NormalizedSignalsTracker L1 + AnomalySignalPanel L3, TC-FR-4.2c-01~08). (2) FR-4.2d 헤더 "번호 정합" 노트를 확정 체계(4.2c=예외·4.2d=Z-Score)로 갱신. (3) FR-4.2에 `detect_capping` 케이스(TC-FR-4.2-08·09) 및 계약에 detect_capping/build_signal_details 추가. (4) FR-1.3에 AliasExtractor 케이스(TC-FR-1.3-06~09). (5) FR-4.4에 redistribute/normalize/match_preset 케이스(TC-FR-4.4-10~14). (6) 부록 B 미커버 목록에 4.2c 추가. 상위 문서 RR v1.5·Architecture v1.3로 갱신.**| 이대한 |
|**v1.3**|**2026-06-01**|**RR v1.6·test-plan v1.3 사용자 피드백(11대 UI/UX 결함 및 기능 방어 요소) 반영. (1) FR-3.1에 카톡 단독 파이프라인(TC-FR-3.1-06) 및 매핑 식별자 100% 표출(TC-FR-3.1-07) 케이스·pytest 스켈레톤 추가. (2) FR-4.4 UI에 가중치 실시간 연동(TC-FR-4.4-15), 숫자 표시(TC-FR-4.4-16), "작업 종류 별 반영 비율" 헤더(TC-FR-4.4-17), 연동 일관성(TC-FR-4.4-18) 케이스·pytest 추가. (3) FR-5.1 placeholder 문구를 "분석할 데이터가 없습니다."로 변경(TC-FR-5.1-01). (4) FR-5.1a 툴팁에 원시값 구성요소 포함(TC-FR-5.1a-03 개정·TC-FR-5.1a-10 신설). (5) FR-5.4에 [새 분석] 입력 초기화(TC-FR-5.4-07·08)·pytest 추가. (6) FR-5.5에 입력 파일명/저장소명 표시(TC-FR-5.5-06~08), 미입력 시 "없음" 표시(TC-FR-5.5-09)·pytest 추가. (7) FR-5.7에 빈 매핑 OK 차단(TC-FR-5.7-07), Cancel 안전 처리(TC-FR-5.7-08), OK 활성 조건(TC-FR-5.7-09), Cancel 후 재사용(TC-FR-5.7-10)·pytest 추가. (8) 부록 A 수동 체크리스트에 아이콘·가중치 연동·placeholder·파일명 표시·입력 초기화·매핑 방어·카톡 단독 항목 추가, 시나리오 D(아이콘) 신설. (9) 부록 B 미커버 목록에 NFR-4.1 추가. 상위 문서 RR v1.6·test-plan v1.3으로 갱신.**| 이대한 |
| **v1.4** | **2026-06-02** | **Capping 한도 상향 반영: FR-4.2의 단일 커밋 추가 라인 제한 기준을 1,000줄에서 50,000줄로 상향함에 따라 관련 테스트 케이스 수정.** | 이대한, 김휘중 공동 작업 |