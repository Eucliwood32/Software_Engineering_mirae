"""
FR-3.1/3.2 MessengerParser 단위 테스트 (L1)
TC-FR-3.1-01 ~ 05, TC-FR-3.2-01 ~ 04
"""
from qce.model.parsing.messenger_parser import MessengerParser


# ── FR-3.1 카카오톡 파싱 ─────────────────────────────────────────────────

def test_basic_parse(katalk):                         # TC-FR-3.1-01
    lines = [("A", "m1"), ("B", "m2"), ("A", "m3")]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 3
    assert res.records[0].author == "A"
    assert res.records[0].message == "m1"
    assert res.records[1].author == "B"


def test_utf8_korean(katalk):                         # TC-FR-3.1-02
    lines = [("홍길동", "안녕하세요")]
    res = MessengerParser().parse(katalk(lines, enc="utf-8"))
    assert res.records[0].author == "홍길동"
    assert res.records[0].message == "안녕하세요"


def test_cp949_korean(katalk):                        # TC-FR-3.1-03
    lines = [("김철수", "반갑습니다")]
    res = MessengerParser().parse(katalk(lines, enc="cp949"))
    assert res.records[0].author == "김철수"
    assert res.records[0].message == "반갑습니다"


def test_date_line_not_in_records(katalk):            # TC-FR-3.1-04
    lines = [("A", "hello")]
    res = MessengerParser().parse(katalk(lines))
    # header_date line is automatically prepended by factory; should not appear in records
    assert all(r.author != "2024년 1월 15일 월요일" for r in res.records)
    assert len(res.records) == 1


def test_message_with_colon_and_bracket(katalk):      # TC-FR-3.1-05
    msg = "URL: https://[example.com]"
    lines = [("A", msg)]
    res = MessengerParser().parse(katalk(lines))
    assert res.records[0].message == msg


def test_multiline_message_merged(katalk):            # TC-FR-3.1-06
    """카톡 멀티라인: 접두사 없는 이어진 본문 줄이 직전 메시지에 병합된다.
    줄바꿈으로 여러 줄 보낸 메시지가 첫 줄만 남고 나머지가 유실되면 안 된다."""
    lines = [
        "[A] [오후 2:30] 첫 줄",
        "둘째 줄",
        "셋째 줄",
        ("B", "답장"),
    ]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 2                       # 멀티라인은 단일 record
    assert res.records[0].author == "A"
    assert res.records[0].message == "첫 줄\n둘째 줄\n셋째 줄"
    assert res.records[1].author == "B"
    assert res.records[1].message == "답장"


def test_multiline_not_counted_as_skip(katalk):       # TC-FR-3.2-05
    """멀티라인 본문 줄은 오염 줄이 아니므로 skipped_lines에 잡히지 않는다."""
    lines = [
        "[A] [오후 2:30] 회의 안건",
        "1. 일정",
        "2. 역할",
        "3. 마일스톤",
    ]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 1
    assert res.skipped_lines == 0
    assert res.records[0].message == "회의 안건\n1. 일정\n2. 역할\n3. 마일스톤"


# ── FR-3.2 오염 줄 방어적 Skip ──────────────────────────────────────────

def test_skip_counts(katalk):                         # TC-FR-3.2-01
    # 오염 줄은 메시지 컨텍스트가 없는 파일 머리(날짜줄 직후)에 둔다.
    # 정상 메시지 '뒤'의 접두사 없는 줄은 카톡 멀티라인 본문이므로 skip이 아니라
    # 직전 메시지로 병합된다(test_multiline_* 참조). FR-3.2 방어 skip은 컨텍스트 없는 오염 줄 대상.
    lines = ["@@깨진줄@@", "??? not valid", "---"] + [("A", "안녕")] * 10
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 10
    assert res.skipped_lines == 3


def test_all_garbage(katalk):                         # TC-FR-3.2-02
    res = MessengerParser().parse(katalk(["xx"] * 100))
    assert res.records == []
    assert res.skipped_lines == 100


def test_empty_file(tmp_path):                        # TC-FR-3.2-03
    p = tmp_path / "empty.txt"
    p.write_text("", encoding="utf-8")
    res = MessengerParser().parse(str(p))
    assert res.records == []
    assert res.skipped_lines == 0


def test_no_exception_on_garbage(katalk):             # TC-FR-3.2-04
    lines = ["@@"] * 50 + [("A", "정상")] * 5
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 5


# ── FR-3.1 식별자 누락 방지 ──────────────────────────────────────────────────

def test_all_authors_preserved_in_records(katalk):   # TC-FR-3.1-07
    """파싱된 모든 발화자가 records에 빠짐없이 포함된다.
    불용어 메시지만 가진 발화자(Bob)도 records에 남아야 한다 — 식별자 누락 방지."""
    lines = [("Alice", "안녕"), ("Bob", "ㅇㅇ"), ("Charlie", "네")]
    res = MessengerParser().parse(katalk(lines))
    authors = {r.author for r in res.records}
    assert {"Alice", "Bob", "Charlie"}.issubset(authors)


def test_author_not_dropped_on_stopword_only_messages(katalk):  # TC-FR-3.1-07 확장
    """불용어로만 발화한 팀원 식별자가 records에서 사라지지 않는다.
    StopwordFilter 이전 단계(MessengerParser)는 author를 절대 버리지 않는다."""
    stopword_only = [("침묵자", "ㄱ"), ("침묵자", "넵"), ("발화자", "오늘 회의록 정리했습니다")]
    res = MessengerParser().parse(katalk(stopword_only))
    authors = {r.author for r in res.records}
    assert "침묵자" in authors
    assert "발화자" in authors


def test_24hour_format(katalk):                         # TC-FR-3.1-08
    lines = [
        "[A] [15:47] 24시간제 메시지",
        "멀티라인",
        "[B] [0:39] 이것도"
    ]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 2
    assert res.records[0].author == "A"
    assert res.records[0].timestamp == "15:47"
    assert res.records[0].message == "24시간제 메시지\n멀티라인"
    assert res.records[1].author == "B"
    assert res.records[1].timestamp == "00:39"


def test_empty_message_body(katalk):                    # TC-FR-3.1-09
    lines = [
        "[A] [오후 5:47] ",
        "첫 줄 비어있는 멀티라인",
        "[B] [10:00]"
    ]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 2
    assert res.records[0].message == "\n첫 줄 비어있는 멀티라인"
    assert res.records[1].message == ""


def test_hyphen_date_format(katalk):                    # TC-FR-3.1-10
    lines = [
        "--------------- 2026년 5월 12일 화요일 ---------------",
        "[A] [12:00] 안녕"
    ]
    res = MessengerParser().parse(katalk(lines))
    assert len(res.records) == 1
    assert res.skipped_lines == 0
