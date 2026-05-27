# Spec 00: 프로젝트 개요 및 아키텍처

> **SSOT (Single Source of Truth)** — 이 파일은 QCE 프로젝트의 전체 아키텍처와 기술적 제약을 정의합니다.
> 변경 시 반드시 팀 합의 + 사용자 승인이 필요합니다.

---

## 프로젝트 정의

**QCE (Quantitative Contribution Evaluator)** — 팀 프로젝트 기여도 정량 평가 도구

- **유형:** Windows 전용 로컬 데스크톱 애플리케이션
- **목적:** 조장이 팀원의 실제 기여도를 데이터 기반으로 정량 평가
- **데이터 소스 3종:** Git 커밋 이력, OOXML 문서 메타데이터, 메신저 대화 로그
- **핵심 제약:** 외부 네트워크 연결 완전 배제, AI API 호출 금지

---

## 아키텍처: MVC 패턴

```
┌──────────────────────────────────────────────────────────┐
│                        QCE 앱                            │
│                                                          │
│   🎨 View (이대한)        🔗 Controller (공동)            │
│   ┌──────────────┐      ┌──────────────────┐            │
│   │ PyQt6 UI     │◄────►│ 이벤트 중재       │            │
│   │ 대시보드/차트  │      │ 데이터 전달       │            │
│   └──────────────┘      └────────┬─────────┘            │
│                                  │                       │
│   ⚙️ Model (조원희 + 김휘중)       ▼                       │
│   ┌────────────────────────────────────────┐            │
│   │ OoxmlParser │ GitParser │ MessengerParser│  ← 백엔드 │
│   ├────────────────────────────────────────┤            │
│   │ Normalizer │ ScoringEngine │ AliasMapper │  ← 로직  │
│   └────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────┘
```

**의존 방향:** View → Controller → Model (단방향만 허용)

---

## 기술 스택

| 영역 | 기술 | 근거 |
|---|---|---|
| 언어 | Python 3.10+ | 팀 공통 |
| UI | PyQt6 | Worker Thread 분리 지원 |
| 문서 파싱 | python-docx, python-pptx | OOXML 직접 파싱 |
| 한국어 NLP | kiwipiepy 또는 soynlp | JRE 의존 없음 (A-4 제약) |
| 테스트 | pytest | 단위 테스트 |
| 패키징 | PyInstaller --onefile | 단일 .exe 배포 (A-1 제약) |

---

## 팀 역할

| 학번 | 이름 | 역할 | 담당 모듈 |
|---|---|---|---|
| 20222047 | 조원희 | 백엔드 | ooxml_parser, git_parser, messenger_parser, cache_manager |
| 20247142 | 이대한 | 프론트엔드 | main_window, dashboard_view, weight_panel, warning_panel |
| 20221985 | 김휘중 | 비즈니스 로직 | normalizer, scoring_engine, alias_mapper, warning_engine |

---

## 가정 및 의존성

| ID | 제약 |
|---|---|
| A-1 | Windows 10/11 x64, PyInstaller --onefile 단일 파일 실행 |
| A-2 | Python 3.10+, PyQt6 (Worker Thread 분리) |
| A-3 | Git 2.x PATH 등록 전제 (미설치 시 안내 팝업) |
| A-4 | JRE 의존 라이브러리 사용 금지 (kiwipiepy/soynlp만 허용) |

---

## 모듈 구조

```
src/
├── backend/
│   ├── __init__.py
│   ├── ooxml_parser.py     # FR-1.1, FR-1.2
│   ├── git_parser.py       # FR-2.1
│   ├── messenger_parser.py # FR-3.1, FR-3.2
│   └── cache_manager.py    # NFR-2.3, NFR-2.4
├── business_logic/
│   ├── __init__.py
│   ├── normalizer.py       # FR-4.1
│   ├── scoring_engine.py   # FR-4.2, FR-4.3
│   ├── weight_manager.py   # FR-4.4
│   ├── alias_mapper.py     # FR-1.2
│   └── warning_engine.py   # FR-4.2 (이상치)
├── frontend/
│   ├── __init__.py
│   ├── main_window.py      # 메인 윈도우 + Drag&Drop
│   ├── dashboard_view.py   # FR-5.1 차트
│   ├── weight_panel.py     # FR-4.4 슬라이더
│   └── report_writer.py    # FR-5.2 리포트 저장
├── analyzer.py             # 오케스트레이터
└── main.py                 # 엔트리포인트
```
