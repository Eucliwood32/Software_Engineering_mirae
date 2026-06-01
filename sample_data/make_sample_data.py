"""샘플 데이터 생성 스크립트 — 가상 팀 프로젝트 "도서관 대출 관리 시스템".

조장이 QCE를 실제로 써 보거나 시연할 때 입력으로 사용할 예시 데이터를 만든다.
ConOps 시나리오 A(학기말 종합 평가)를 그대로 재현하며, 다음 3개 기능이 결과
화면에서 분명히 드러나도록 데이터를 의도적으로 설계했다.

    - EW-02 버스트 커밋   : 최민호가 마감일에 동일 시각으로 다수 커밋
    - Z-score 하위 이상치 : 정유나가 git·문서·메신저 모두 최저
    - 계정 병합           : 이지은이 소스마다 다른 식별자 사용
                            (git=jelee@lib.dev / 문서=Jieun Lee / 카톡=이지은)

실행:
    python sample_data/make_sample_data.py

생성 결과:
    sample_data/docs/   기획서.docx 외 docx 4 · pptx 3 · hwpx 1 (총 8개)
    sample_data/chat/kakao_chat.txt
    sample_data/repo/   (Git 저장소)

* 카카오톡/Git은 시간대 다양화·버스트 커밋이 필요하므로 이 스크립트의 전용
  함수로 생성한다(문서는 tests/fixtures/factories의 팩토리를 재사용).
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys

# 프로젝트 루트를 경로에 추가 (팩토리 import용)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.fixtures.factories import make_docx, make_hwpx, make_pptx  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(BASE, "docs")
CHAT = os.path.join(BASE, "chat")
REPO = os.path.join(BASE, "repo")


# ════════════════════════════════════════════════════════════════════════════
# 1. 문서 (docx × 4, pptx × 3, hwpx × 1)
#    작성자 메타데이터가 곧 기여자 식별자가 된다(파서가 author/last_modified_by/
#    dc:creator를 추출). 글자수(공백 제외)는 박서준·이지은·최민호가 충분히 크고
#    서로 비슷하게, 정유나는 0(문서 미작성)이 되도록 분량을 조절했다.
# ════════════════════════════════════════════════════════════════════════════

# ── 박서준 기획서 (docx) ──────────────────────────────────────────────────
PLAN_TEXT = (
    "도서관 대출 관리 시스템 기획서\n\n"
    "1. 프로젝트 개요\n"
    "본 프로젝트는 교내 도서관의 도서 대출과 반납 업무를 전산화하여 이용자 편의를 높이고 "
    "사서의 업무 부담을 줄이는 것을 목표로 한다. 기존에는 종이 대장으로 대출 기록을 관리하여 "
    "도서 검색과 연체 확인에 많은 시간이 소요되었으며, 분실 도서를 추적하기도 어려웠다. "
    "본 시스템은 도서 검색, 대출, 반납, 연체 알림, 회원 관리 기능을 하나의 화면에서 제공한다.\n\n"
    "2. 개발 범위\n"
    "가. 도서 검색: 제목, 저자, 출판사, 분류 기호로 소장 도서를 빠르게 조회한다.\n"
    "나. 대출 및 반납: 회원증 번호와 도서 바코드를 입력하면 대출 상태가 즉시 갱신된다.\n"
    "다. 연체 관리: 반납 예정일이 지난 도서를 자동으로 식별하고 연체료를 산정한다.\n"
    "라. 회원 관리: 회원 가입, 정보 수정, 대출 이력 조회 기능을 제공한다.\n\n"
    "3. 개발 일정\n"
    "1주차에는 요구사항을 분석하고 화면 설계를 확정한다. 2주차에는 데이터베이스 스키마를 "
    "설계하고 대출 및 반납의 핵심 로직을 구현한다. 3주차에는 검색과 연체 알림 기능을 붙이고 "
    "화면을 연동한다. 4주차에는 통합 테스트와 사용자 매뉴얼 작성을 마무리한다.\n\n"
    "4. 기대 효과\n"
    "대출 업무 처리 시간이 단축되고 연체 도서를 체계적으로 관리할 수 있게 되어 도서관 운영의 "
    "정확성과 효율이 함께 향상될 것으로 기대한다.\n"
)

# ── 이지은 요구사항명세서 (docx, 작성자 = Jieun Lee) ──────────────────────
REQ_TEXT = (
    "도서관 대출 관리 시스템 요구사항 명세서\n\n"
    "1. 목적\n"
    "본 문서는 도서관 대출 관리 시스템이 제공해야 하는 기능 요구사항과 비기능 요구사항을 "
    "정의한다. 모든 요구사항은 검증 가능하도록 구체적으로 기술하며, 설계와 테스트의 기준이 된다.\n\n"
    "2. 기능 요구사항\n"
    "FR-1 도서 검색: 사용자는 제목, 저자, 분류 기호의 일부만 입력해도 일치하는 도서 목록을 "
    "조회할 수 있어야 한다. 검색 결과에는 소장 위치와 대출 가능 여부가 함께 표시된다.\n"
    "FR-2 대출 처리: 사서는 회원과 도서를 선택하여 대출을 등록할 수 있어야 하며, 1인당 동시 "
    "대출 가능 권수는 다섯 권으로 제한한다. 이미 대출 중인 도서는 다시 대출할 수 없다.\n"
    "FR-3 반납 처리: 반납 시 대출 상태가 즉시 해제되고 도서가 다시 검색 결과에 노출된다.\n"
    "FR-4 연체 관리: 반납 예정일이 지난 대출 건은 연체로 표시하고, 하루 단위로 연체료를 "
    "누적한다. 연체 회원에게는 대출이 일시적으로 제한된다.\n"
    "FR-5 회원 관리: 회원의 가입과 정보 수정, 대출 이력 조회를 지원한다.\n\n"
    "3. 비기능 요구사항\n"
    "NFR-1 응답 시간: 도서 검색 결과는 2초 이내에 표시되어야 한다.\n"
    "NFR-2 사용성: 사서가 별도 교육 없이 30분 이내에 기본 업무를 수행할 수 있어야 한다.\n"
    "NFR-3 신뢰성: 대출과 반납 기록은 어떤 경우에도 누락되거나 중복되지 않아야 한다.\n\n"
    "4. 제약 사항\n"
    "시스템은 교내 네트워크에서만 동작하며, 외부로 회원 개인정보를 전송하지 않는다.\n"
)

# ── 최민호 설계서 (docx) ─────────────────────────────────────────────────
DESIGN_TEXT = (
    "도서관 대출 관리 시스템 설계서\n\n"
    "1. 아키텍처 개요\n"
    "시스템은 표현 계층, 업무 로직 계층, 데이터 접근 계층의 3계층 구조로 구성한다. 표현 계층은 "
    "사서가 사용하는 화면을 담당하고, 업무 로직 계층은 대출과 반납 규칙을 처리하며, 데이터 "
    "접근 계층은 도서와 회원, 대출 기록을 데이터베이스에 저장하고 조회한다.\n\n"
    "2. 데이터 모델\n"
    "도서 테이블은 도서 번호, 제목, 저자, 분류 기호, 대출 상태를 가진다. 회원 테이블은 회원 "
    "번호, 이름, 연락처, 가입일을 가진다. 대출 테이블은 대출 번호, 도서 번호, 회원 번호, 대출일, "
    "반납 예정일, 실제 반납일을 가지며 연체 여부는 반납 예정일과 현재 날짜를 비교하여 계산한다.\n\n"
    "3. 핵심 로직\n"
    "대출 등록 시 회원의 현재 대출 권수와 연체 여부를 먼저 확인한다. 조건을 만족하면 대출 "
    "기록을 생성하고 도서 상태를 대출 중으로 변경한다. 반납 시에는 반납일을 기록하고 도서 "
    "상태를 복구하며, 연체된 경우 연체료를 산정하여 회원에게 안내한다.\n"
)

# ── 최민호 회의록 (docx) ─────────────────────────────────────────────────
MINUTES_TEXT = (
    "프로젝트 정기 회의록\n\n"
    "일시: 2024년 9월 23일 오후 7시\n"
    "참석자: 박서준, 이지은, 최민호, 정유나\n\n"
    "안건 1. 역할 분담 확정\n"
    "백엔드와 대출 로직은 박서준이, 화면과 사용자 연동은 이지은이 담당한다. 설계 문서와 "
    "발표 자료, 사용자 매뉴얼 작성은 최민호가 맡는다. 정유나는 테스트 데이터 준비를 돕기로 했다.\n\n"
    "안건 2. 일정 점검\n"
    "다음 주까지 요구사항 명세를 확정하고, 데이터베이스 스키마 초안을 공유하기로 했다. "
    "중간 발표 전까지 대출과 반납의 기본 흐름을 동작 가능한 수준으로 완성한다.\n\n"
    "안건 3. 협업 도구\n"
    "코드는 깃 저장소로 관리하고, 일정과 논의는 단체 채팅방을 통해 공유한다.\n"
)

# ── 최민호 중간발표 (pptx) ───────────────────────────────────────────────
MID_SLIDES = [
    ["도서관 대출 관리 시스템", "중간 발표 자료", "발표자 최민호"],
    [
        "추진 배경",
        "종이 대장 기반 대출 관리의 한계",
        "검색과 연체 확인에 과도한 시간 소요",
        "분실 도서 추적의 어려움",
    ],
    [
        "지금까지의 진행 상황",
        "요구사항 명세와 화면 설계 완료",
        "도서 검색과 대출 등록 기능 구현",
        "데이터베이스 스키마 확정",
    ],
    [
        "남은 일정",
        "반납과 연체 알림 기능 구현",
        "화면 연동과 통합 테스트",
        "사용자 매뉴얼 작성",
    ],
]

# ── 이지은 최종발표 (pptx, 작성자 = Jieun Lee) ────────────────────────────
FINAL_SLIDES = [
    ["도서관 대출 관리 시스템", "최종 발표 자료", "발표자 이지은"],
    [
        "완성된 기능 요약",
        "도서 검색 제목 저자 분류 기호 지원",
        "대출과 반납 상태 실시간 반영",
        "연체 자동 식별과 연체료 산정",
        "회원 가입과 대출 이력 조회",
    ],
    [
        "화면 구성",
        "검색 화면에서 소장 위치와 대출 가능 여부 표시",
        "대출 화면에서 회원과 도서를 선택해 즉시 등록",
        "연체 현황 화면에서 기한 초과 도서 한눈에 확인",
    ],
    [
        "사용자 평가 결과",
        "사서 업무 처리 시간 절반으로 단축",
        "별도 교육 없이 기본 업무 수행 가능",
        "연체 도서 관리의 정확성 향상",
    ],
    [
        "향후 개선 방향",
        "도서 예약 대기 기능 추가",
        "모바일 화면 지원",
        "통계 리포트 자동 생성",
    ],
]

# ── 박서준 시연 시나리오 (pptx) ──────────────────────────────────────────
DEMO_SLIDES = [
    ["시연 시나리오", "도서관 대출 관리 시스템", "작성 박서준"],
    [
        "시나리오 1 도서 대출",
        "회원증 번호 입력 후 회원 확인",
        "도서 바코드 입력으로 대출 등록",
        "반납 예정일 자동 계산 확인",
    ],
    [
        "시나리오 2 도서 반납과 연체",
        "반납 도서 바코드 입력",
        "연체 도서의 연체료 산정 확인",
        "연체 회원 대출 제한 동작 확인",
    ],
]

# ── 최민호 사용자 매뉴얼 (hwpx, 작성자 = dc:creator 최민호) ────────────────
MANUAL_TEXT = (
    "도서관 대출 관리 시스템 사용자 매뉴얼\n\n"
    "1. 시작하기\n"
    "프로그램을 실행하면 검색 화면이 가장 먼저 표시된다. 상단 입력창에 도서 제목이나 저자의 "
    "일부를 입력하고 검색 단추를 누르면 일치하는 도서 목록이 나타난다.\n\n"
    "2. 도서 대출하기\n"
    "대출 화면으로 이동하여 회원증 번호를 입력하고 회원을 확인한 뒤, 대출할 도서의 바코드를 "
    "입력한다. 대출이 등록되면 반납 예정일이 화면에 표시된다. 한 회원은 최대 다섯 권까지 동시에 "
    "대출할 수 있다.\n\n"
    "3. 도서 반납하기\n"
    "반납 화면에서 도서 바코드를 입력하면 대출 상태가 해제된다. 반납 예정일이 지난 도서는 "
    "연체료가 함께 안내된다.\n\n"
    "4. 자주 묻는 질문\n"
    "연체 중인 회원은 연체료를 정산하고 도서를 반납하기 전까지 새로운 대출이 제한된다.\n"
)


def _build_documents() -> None:
    make_docx(os.path.join(DOCS, "기획서.docx"), "박서준", PLAN_TEXT)
    make_docx(os.path.join(DOCS, "요구사항명세서.docx"), "Jieun Lee", REQ_TEXT)
    make_docx(os.path.join(DOCS, "설계서.docx"), "최민호", DESIGN_TEXT)
    make_docx(os.path.join(DOCS, "회의록.docx"), "최민호", MINUTES_TEXT)
    make_pptx(os.path.join(DOCS, "중간발표.pptx"), "최민호", MID_SLIDES)
    make_pptx(os.path.join(DOCS, "최종발표.pptx"), "Jieun Lee", FINAL_SLIDES)
    make_pptx(os.path.join(DOCS, "시연시나리오.pptx"), "박서준", DEMO_SLIDES)
    make_hwpx(os.path.join(DOCS, "사용자매뉴얼.hwpx"), "최민호", MANUAL_TEXT)
    for name in (
        "기획서.docx", "요구사항명세서.docx", "설계서.docx", "회의록.docx",
        "중간발표.pptx", "최종발표.pptx", "시연시나리오.pptx", "사용자매뉴얼.hwpx",
    ):
        print(f"  OK docs/{name}")


# ════════════════════════════════════════════════════════════════════════════
# 2. 카카오톡 대화 (학기 단위, 시간대 다양화)
#    형식: 날짜 구분줄 + "[이름] [오전|오후 H:MM] 메시지"
#    발화 분포(총 줄 수): 박서준 ≫ 이지은 ≳ 최민호 ≫ 정유나(최소).
#    이지은은 카톡에서 "이지은"으로 표시되어 git/문서 식별자와 분리된다.
#    ㅇㅋ·ㅋㅋ·(이모티콘)·네 등은 불용어로 분류되어 CLI 유효 발화 수에서 제외된다.
# ════════════════════════════════════════════════════════════════════════════

# (kind, *args)
#   ("date", "YYYY년 M월 D일 요일")
#   ("msg", 이름, "오전|오후 H:MM", 메시지)
CHAT_SCRIPT = [
    ("date", "2024년 9월 9일 월요일"),
    ("msg", "박서준", "오후 7:02", "이번 학기 팀 프로젝트 주제 도서관 대출 관리 시스템으로 가시죠"),
    ("msg", "이지은", "오후 7:05", "좋아요 도서관 자주 쓰는데 불편한 점이 많았어요"),
    ("msg", "최민호", "오후 7:06", "저도 찬성입니다 자료 조사부터 시작할까요"),
    ("msg", "박서준", "오후 7:08", "네 각자 비슷한 시스템 사례 하나씩 찾아서 내일 공유해요"),
    ("msg", "정유나", "오후 7:20", "넵"),
    ("msg", "이지은", "오후 7:22", "화면 흐름은 제가 한번 그려볼게요"),
    ("msg", "박서준", "오후 7:25", "좋습니다 그럼 역할은 회의 때 확정하죠"),

    ("date", "2024년 9월 16일 월요일"),
    ("msg", "박서준", "오전 10:11", "요구사항 초안 정리했는데 검색 대출 반납 연체 회원관리 다섯 기능으로 잡았어요"),
    ("msg", "이지은", "오전 10:15", "명세서는 제가 맡아서 상세하게 써볼게요"),
    ("msg", "최민호", "오전 10:18", "설계 문서랑 발표자료는 제가 담당할게요"),
    ("msg", "박서준", "오전 10:20", "대출 반납 핵심 로직이랑 백엔드는 제가 할게요"),
    ("msg", "이지은", "오전 10:21", "화면이랑 연동은 제가요"),
    ("msg", "최민호", "오전 10:24", "정유나님은 테스트 데이터 준비 부탁드려도 될까요"),
    ("msg", "정유나", "오후 1:40", "네 알겠습니다"),
    ("msg", "박서준", "오후 1:45", "ㅇㅋ 그럼 다음주까지 명세 확정합시다"),

    ("date", "2024년 9월 23일 월요일"),
    ("msg", "최민호", "오후 7:00", "오늘 회의록 정리해서 올렸습니다 확인 부탁드려요"),
    ("msg", "박서준", "오후 7:03", "확인했어요 스키마 초안도 곧 공유할게요"),
    ("msg", "이지은", "오후 7:05", "검색 화면 목업 거의 다 됐어요"),
    ("msg", "이지은", "오후 7:06", "(이모티콘)"),
    ("msg", "최민호", "오후 7:09", "오 좋네요 발표자료에 반영할게요"),
    ("msg", "박서준", "오후 7:12", "대출 등록 로직 먼저 짜고 있는데 동시 대출 다섯 권 제한 넣었어요"),
    ("msg", "최민호", "오후 7:14", "ㅋㅋ 역시 빠르시네요"),

    ("date", "2024년 10월 7일 월요일"),
    ("msg", "박서준", "오후 9:01", "대출 반납 기본 흐름 커밋했어요 검색이랑 붙이면 중간발표 데모 가능할 듯"),
    ("msg", "이지은", "오후 9:04", "검색 화면 연동 오늘 밤에 마무리할게요"),
    ("msg", "최민호", "오후 9:07", "중간발표 자료 초안 잡았습니다"),
    ("msg", "박서준", "오후 9:10", "고생 많으십니다 데모 시나리오는 제가 정리할게요"),
    ("msg", "이지은", "오후 11:32", "검색 연동 끝났어요 푸시했습니다"),
    ("msg", "박서준", "오후 11:35", "확인했어요 깔끔하네요"),

    ("date", "2024년 10월 14일 월요일"),
    ("msg", "최민호", "오후 2:10", "중간발표 잘 끝났습니다 다들 수고하셨어요"),
    ("msg", "박서준", "오후 2:12", "수고하셨습니다 이제 연체 기능 들어가죠"),
    ("msg", "이지은", "오후 2:15", "연체 현황 화면 제가 그릴게요"),
    ("msg", "정유나", "오후 2:30", "테스트용 회원 데이터 50건 만들어서 공유했어요"),
    ("msg", "박서준", "오후 2:33", "오 감사합니다 바로 써볼게요"),

    ("date", "2024년 11월 4일 월요일"),
    ("msg", "박서준", "오후 8:05", "연체료 산정 로직 추가했어요 하루 단위로 누적되게"),
    ("msg", "이지은", "오후 8:08", "연체 화면에서 잘 보이게 색으로 강조해뒀어요"),
    ("msg", "최민호", "오후 8:11", "사용자 매뉴얼도 쓰기 시작했습니다"),
    ("msg", "박서준", "오후 8:14", "좋네요 통합 테스트 항목 같이 정리해봐요"),
    ("msg", "이지은", "오후 8:16", "넵 제가 표로 만들게요"),
    ("msg", "최민호", "오후 8:20", "ㅇㅋ"),

    ("date", "2024년 11월 25일 월요일"),
    ("msg", "박서준", "오후 9:40", "통합 테스트 돌렸는데 반납 처리에서 버그 하나 잡았어요 수정 푸시함"),
    ("msg", "이지은", "오후 9:43", "화면 쪽도 자잘한 거 몇 개 고쳤어요"),
    ("msg", "최민호", "오후 9:45", "최종 발표자료 거의 완성했습니다"),
    ("msg", "박서준", "오후 9:47", "수고 많으십니다 마무리 잘 해봐요"),

    ("date", "2024년 12월 9일 월요일"),
    ("msg", "최민호", "오후 11:25", "마감 전에 매뉴얼이랑 테스트 코드 정리해서 한번에 올릴게요"),
    ("msg", "박서준", "오후 11:30", "넵 고생하세요"),
    ("msg", "이지은", "오후 11:33", "최종 발표 PPT 올렸습니다"),
    ("msg", "최민호", "오후 11:55", "정리 끝났어요 다 푸시했습니다 다들 수고 많으셨습니다"),
    ("msg", "박서준", "오후 11:58", "수고하셨습니다 발표 준비만 남았네요"),
    ("msg", "이지은", "오후 11:59", "ㅋㅋ 드디어 끝"),
]


def _serialize_chat(script: list) -> str:
    lines: list[str] = []
    for item in script:
        if item[0] == "date":
            lines.append(item[1])
        else:
            _, author, time_str, msg = item
            lines.append(f"[{author}] [{time_str}] {msg}")
    return "\n".join(lines) + "\n"


def _build_chat() -> None:
    os.makedirs(CHAT, exist_ok=True)
    path = os.path.join(CHAT, "kakao_chat.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(_serialize_chat(CHAT_SCRIPT))
    print("  OK chat/kakao_chat.txt")


# ════════════════════════════════════════════════════════════════════════════
# 3. Git 저장소
#    Git은 author email(%ae)로 집계된다. 박서준/최민호/정유나는 email을 순수
#    한글 이름으로 두어 문서·카톡 식별자와 자동으로 합쳐지게 하고, 이지은만
#    jelee@lib.dev 를 써서 문서(Jieun Lee)·카톡(이지은)과 분리 → 병합 데모.
#
#    EW-02: 최민호의 버스트 커밋 7개는 모두 동일한 author/committer date를
#           가진다(%ai 문자열이 같아야 한 버킷으로 묶여 신호가 발화).
#    Capping 회피: 단일 커밋 additions ≤ 150 으로 유지(1000줄 초과 없음).
# ════════════════════════════════════════════════════════════════════════════

_BURST_TS = "2024-12-09T23:30:00+09:00"  # 최민호 버스트 — 전부 동일 타임스탬프

# 각 커밋: (이름, email, author_date, additions, 메시지)
COMMITS = [
    # ── 박서준 (조장, 백엔드) — 최상위 기여, 버스트 없음, 합계 900 ──
    ("박서준", "박서준", "2024-09-12T09:10:00+09:00", 120, "프로젝트 구조 초기화"),
    ("박서준", "박서준", "2024-09-18T14:20:00+09:00", 80,  "도서 회원 대출 엔티티 정의"),
    ("박서준", "박서준", "2024-09-24T10:05:00+09:00", 150, "대출 등록 핵심 로직 구현"),
    ("박서준", "박서준", "2024-10-02T16:40:00+09:00", 90,  "동시 대출 권수 제한 추가"),
    ("박서준", "박서준", "2024-10-07T21:00:00+09:00", 60,  "반납 처리 흐름 구현"),
    ("박서준", "박서준", "2024-10-21T11:30:00+09:00", 110, "검색 쿼리 최적화"),
    ("박서준", "박서준", "2024-11-04T20:00:00+09:00", 70,  "연체료 산정 로직 추가"),
    ("박서준", "박서준", "2024-11-12T13:15:00+09:00", 40,  "연체 회원 대출 제한"),
    ("박서준", "박서준", "2024-11-25T21:40:00+09:00", 90,  "반납 처리 버그 수정"),
    ("박서준", "박서준", "2024-12-02T15:00:00+09:00", 50,  "데이터 접근 계층 리팩터링"),
    ("박서준", "박서준", "2024-12-06T18:25:00+09:00", 40,  "예외 처리 보강"),

    # ── 이지은 (프론트엔드) — git은 jelee@lib.dev, 합계 700 ──
    ("jelee", "jelee@lib.dev", "2024-09-20T22:10:00+09:00", 120, "검색 화면 레이아웃"),
    ("jelee", "jelee@lib.dev", "2024-09-27T20:30:00+09:00", 90,  "도서 목록 컴포넌트"),
    ("jelee", "jelee@lib.dev", "2024-10-07T23:20:00+09:00", 150, "검색 결과 연동"),
    ("jelee", "jelee@lib.dev", "2024-10-15T19:45:00+09:00", 80,  "대출 화면 구현"),
    ("jelee", "jelee@lib.dev", "2024-11-04T20:10:00+09:00", 110, "연체 현황 화면"),
    ("jelee", "jelee@lib.dev", "2024-11-25T21:30:00+09:00", 100, "화면 버그 수정"),
    ("jelee", "jelee@lib.dev", "2024-12-08T17:00:00+09:00", 50,  "최종 화면 정리"),

    # ── 최민호 (문서·발표 리드) — 일반 커밋 6 + 마감일 버스트 7, 합계 590 ──
    ("최민호", "최민호", "2024-09-25T13:00:00+09:00", 60, "데이터베이스 스키마 정의"),
    ("최민호", "최민호", "2024-10-08T15:30:00+09:00", 70, "검색 서비스 골격"),
    ("최민호", "최민호", "2024-10-22T16:10:00+09:00", 50, "분류 기호 검색 지원"),
    ("최민호", "최민호", "2024-11-05T14:50:00+09:00", 80, "연체 판정 유틸 추가"),
    ("최민호", "최민호", "2024-11-19T17:20:00+09:00", 60, "테스트 코드 초안"),
    ("최민호", "최민호", "2024-12-03T11:40:00+09:00", 70, "매뉴얼용 예제 데이터"),
    # 마감일 버스트 (동일 타임스탬프 7개) → EW-02
    ("최민호", "최민호", _BURST_TS, 30, "테스트 코드 정리 1"),
    ("최민호", "최민호", _BURST_TS, 35, "테스트 코드 정리 2"),
    ("최민호", "최민호", _BURST_TS, 25, "매뉴얼 반영 1"),
    ("최민호", "최민호", _BURST_TS, 30, "매뉴얼 반영 2"),
    ("최민호", "최민호", _BURST_TS, 20, "오타 수정"),
    ("최민호", "최민호", _BURST_TS, 30, "주석 보강"),
    ("최민호", "최민호", _BURST_TS, 25, "최종 정리"),

    # ── 정유나 (보조) — 기여 최저(Z-score 하위), 합계 30 ──
    ("정유나", "정유나", "2024-10-14T13:50:00+09:00", 20, "테스트용 회원 데이터 추가"),
    ("정유나", "정유나", "2024-11-18T16:00:00+09:00", 10, "샘플 도서 목록 보강"),
]


def _force_remove(func, path, _exc) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


# 커밋 메시지 → 대상 파일 (역할에 맞는 도서관 시스템 소스 트리)
_FILE_BY_MESSAGE = {
    "프로젝트 구조 초기화": "README.md",
    "도서 회원 대출 엔티티 정의": "src/models.py",
    "대출 등록 핵심 로직 구현": "src/loan_service.py",
    "동시 대출 권수 제한 추가": "src/loan_service.py",
    "반납 처리 흐름 구현": "src/loan_service.py",
    "검색 쿼리 최적화": "src/repository.py",
    "연체료 산정 로직 추가": "src/loan_service.py",
    "연체 회원 대출 제한": "src/loan_service.py",
    "반납 처리 버그 수정": "src/loan_service.py",
    "데이터 접근 계층 리팩터링": "src/repository.py",
    "예외 처리 보강": "src/exceptions.py",
    "검색 화면 레이아웃": "src/views/search_view.py",
    "도서 목록 컴포넌트": "src/views/book_list.py",
    "검색 결과 연동": "src/views/search_view.py",
    "대출 화면 구현": "src/views/loan_view.py",
    "연체 현황 화면": "src/views/overdue_view.py",
    "화면 버그 수정": "src/views/loan_view.py",
    "최종 화면 정리": "src/views/search_view.py",
    "데이터베이스 스키마 정의": "db/schema.sql",
    "검색 서비스 골격": "src/search.py",
    "분류 기호 검색 지원": "src/search.py",
    "연체 판정 유틸 추가": "src/utils/overdue.py",
    "테스트 코드 초안": "tests/test_loan.py",
    "매뉴얼용 예제 데이터": "docs/manual_examples.md",
    "테스트 코드 정리 1": "tests/test_loan.py",
    "테스트 코드 정리 2": "tests/test_search.py",
    "매뉴얼 반영 1": "docs/user_manual.md",
    "매뉴얼 반영 2": "docs/user_manual.md",
    "오타 수정": "README.md",
    "주석 보강": "src/search.py",
    "최종 정리": "tests/test_loan.py",
    "테스트용 회원 데이터 추가": "data/sample_members.csv",
    "샘플 도서 목록 보강": "data/sample_books.csv",
}

_FILE_TITLES = {
    "models.py": "도메인 모델(Book·Member·Loan)",
    "loan_service.py": "대출·반납·연체 처리 서비스",
    "repository.py": "데이터 접근 계층",
    "exceptions.py": "도메인 예외",
    "search.py": "도서 검색 서비스",
    "overdue.py": "연체 판정 유틸",
    "search_view.py": "검색 화면",
    "book_list.py": "도서 목록 컴포넌트",
    "loan_view.py": "대출 화면",
    "overdue_view.py": "연체 현황 화면",
    "test_loan.py": "대출 서비스 테스트",
    "test_search.py": "검색 서비스 테스트",
}


def _kind_of(relpath: str) -> str:
    if relpath.endswith(".md"):
        return "md"
    if relpath.endswith(".sql"):
        return "sql"
    if relpath.endswith(".csv"):
        return "csv_member" if "member" in relpath else "csv_book"
    if "/views/" in relpath:
        return "view"
    if relpath.startswith("tests/"):
        return "test"
    return "service"


def _header(kind: str, relpath: str) -> list[str]:
    title = _FILE_TITLES.get(relpath.rsplit("/", 1)[-1], relpath.rsplit("/", 1)[-1])
    if kind == "md":
        return ["# 도서관 대출 관리 시스템", "",
                "교내 도서관의 대출·반납·연체·회원 관리를 전산화하는 프로젝트.", ""]
    if kind == "sql":
        return ["-- 도서관 대출 관리 시스템 스키마 (SQLite)", ""]
    if kind == "csv_member":
        return ["회원번호,이름,연락처,가입일"]
    if kind == "csv_book":
        return ["도서번호,제목,저자,분류기호,대출가능"]
    if kind == "view":
        return [f'"""{title} — PyQt6 화면."""',
                "from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QLineEdit", ""]
    if kind == "test":
        return [f'"""{title}."""',
                "from src.loan_service import LoanService",
                "from tests.fakes import FakeRepo", ""]
    return [f'"""{title} — 도서관 대출 관리 시스템."""',
            "from __future__ import annotations",
            "from datetime import date",
            "from src.models import Book, Member, Loan  # noqa: F401",
            "", "MAX_LOAN = 5", "DAILY_FINE = 100", ""]


def _block(kind: str, i: int) -> list[str]:
    if kind == "md":
        return [f"## 기능 {i}", "",
                f"- FR-{i}: 검색/대출/반납/연체/회원 관리 중 세부 기능 {i}을 정의한다.",
                "- 입력 검증과 예외 흐름, 화면 표시 규칙을 함께 기술한다.", ""]
    if kind == "sql":
        return [f"CREATE TABLE IF NOT EXISTS entity_{i} (",
                "    id       INTEGER PRIMARY KEY,",
                "    name     TEXT NOT NULL,",
                f"    ref_code TEXT,           -- 관련 엔티티 {i}",
                "    created  TEXT DEFAULT (datetime('now'))",
                ");", ""]
    if kind == "csv_member":
        return [f"M{i:04d},회원{i},010-{1000 + i:04d}-{2000 + i:04d},2024-03-{(i % 27) + 1:02d}"]
    if kind == "csv_book":
        return [f"B{i:04d},도서제목{i},저자{i % 30},{800 + i % 100},Y"]
    if kind == "view":
        return [f"class Panel{i}(QWidget):",
                f'    """화면 구성요소 {i}."""',
                "    def __init__(self, parent=None):",
                "        super().__init__(parent)",
                "        layout = QVBoxLayout(self)",
                "        self.search_box = QLineEdit()",
                "        self.table = QTableView()",
                "        layout.addWidget(self.search_box)",
                "        layout.addWidget(self.table)", ""]
    if kind == "test":
        return [f"def test_rule_{i}():",
                "    svc = LoanService(FakeRepo())",
                f"    loan = svc.register_loan('B{i:03d}', 'M{i:03d}')",
                f"    assert loan.member_id == 'M{i:03d}'",
                "    assert loan.book_id.startswith('B')", ""]
    return [f"def rule_{i}(self, book_id: str, member_id: str) -> Loan:",
            f'    """대출/반납 규칙 {i}을 적용한다."""',
            "    if self._repo.count_active(member_id) >= MAX_LOAN:",
            "        raise LoanLimitExceeded(member_id)",
            "    if self._repo.find_active(book_id) is not None:",
            "        raise AlreadyLoaned(book_id)",
            "    loan = Loan(book_id, member_id, date.today())",
            "    self._repo.save(loan)",
            "    return loan", ""]


def _content_for(relpath: str, n: int, state: dict) -> list[str]:
    """relpath 파일에 추가할 '정확히 n줄'의 그럴듯한 내용을 만든다(첫 커밋만 헤더)."""
    kind = _kind_of(relpath)
    seq = state.get(relpath, 0)
    lines: list[str] = list(_header(kind, relpath)) if seq == 0 else []
    i = seq * 50 + 1
    while len(lines) < n:
        lines.extend(_block(kind, i))
        i += 1
    state[relpath] = seq + 1
    return lines[:n]


def _build_git_repo() -> None:
    if os.path.exists(REPO):
        shutil.rmtree(REPO, onexc=_force_remove)
    os.makedirs(REPO, exist_ok=True)

    subprocess.run(["git", "init", "-q", REPO], check=True)
    subprocess.run(["git", "-C", REPO, "config", "user.email", "setup@lib.dev"], check=True)
    subprocess.run(["git", "-C", REPO, "config", "user.name", "Setup"], check=True)

    state: dict[str, int] = {}
    for name, email, date_str, additions, message in COMMITS:
        relpath = _FILE_BY_MESSAGE[message]
        target = os.path.join(REPO, *relpath.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        lines = _content_for(relpath, additions, state)   # 정확히 additions줄
        with open(target, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email, "GIT_AUTHOR_DATE": date_str,
            "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email, "GIT_COMMITTER_DATE": date_str,
        }
        subprocess.run(["git", "-C", REPO, "add", "."], check=True, env=env)
        subprocess.run(["git", "-C", REPO, "commit", "-q", "-m", message], check=True, env=env)

    n_files = len({_FILE_BY_MESSAGE[c[4]] for c in COMMITS})
    print(f"  OK repo/ (커밋 {len(COMMITS)}개 · 파일 {n_files}개)")


# ════════════════════════════════════════════════════════════════════════════
# main
# ════════════════════════════════════════════════════════════════════════════
def _reset_dir(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path, onexc=_force_remove)
    os.makedirs(path, exist_ok=True)


def main() -> None:
    print("샘플 데이터 생성 중... (도서관 대출 관리 시스템)")
    _reset_dir(DOCS)
    _reset_dir(CHAT)
    _build_documents()
    _build_chat()
    _build_git_repo()

    print("\n완료! 생성 경로:")
    print(f"  문서: {DOCS}  (docx 4 · pptx 3 · hwpx 1)")
    print(f"  채팅: {os.path.join(CHAT, 'kakao_chat.txt')}")
    print(f"  Git : {REPO}")
    print("\n시연 포인트: 최민호=EW-02 버스트 · 정유나=Z-score 하위 · 이지은=계정 병합")


if __name__ == "__main__":
    main()
