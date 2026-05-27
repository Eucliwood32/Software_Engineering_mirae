# 25학년 1학기 소프트웨어공학 프로젝트 - 커리어 로드맵
Hanbat National University SE Course (2025-1) | Edu-Tech Team Project

팀 구성
지도교수 : 최창범 교수님
참여학생 : 20222047 조원희
20247142 이대한
20221985 김휘중

# ⚓ QCE (부탁해 꼬마선장)
**Windows 전용 Python 데스크톱 팀기여도 정량평가 앱**

QCE(Quantitative Contribution Evaluator)는 팀 프로젝트 내에서의 기여도를 Git 로그, OOXML 문서(Word, PowerPoint), 그리고 메신저 대화 데이터를 기반으로 정량적으로 분석하여 시각화하는 Windows 전용 데스크톱 애플리케이션입니다.

## 🚀 주요 특징 (4대 원칙)
- **O-1 통합분석:** Git 커밋, OOXML 문서 작업량, 메신저 활동량을 단일 파이프라인으로 통합 분석합니다.
- **O-2 어뷰징 방지:** 대량의 단순 코드 삽입 등을 방지하기 위한 Capping(1000줄 제한) 및 로그 스케일링(Log Scaling) 기법을 적용합니다.
- **O-3 시각화 및 리포트:** 분석된 데이터를 막대 차트와 레이더 차트로 시각화하며, `.md` 및 `.csv` 형식의 리포트 저장을 지원합니다.
- **O-4 완전 로컬 실행:** 네트워크 통신을 배제(0byte)하고 로컬 CPU/RAM만 사용하여 데이터 프라이버시를 보장합니다.

## 👥 팀 구성 및 역할
| 이름 | 역할 | 주요 담당 모듈 |
| :--- | :--- | :--- |
| **조원희** | Backend | OOXML 파서, Git 분석, 메신저 파서, 인코딩 처리 |
| **이대한** | Frontend | PyQt6 UI, Worker Thread, 차트 시각화, 프리셋 관리 |
| **김휘중** | Business Logic | 정규화, Capping, 가중치 재계산, 캐시 관리, 모듈 격리 |

## 🛠 기술 스택
- **언어:** Python 3.10+
- **UI:** PyQt6 / PySide6 (Worker Thread 지원)
- **시각화:** matplotlib
- **파싱:** python-docx, python-pptx, csv, subprocess
- **NLP:** kiwipiepy, soynlp (Pure Python)
- **빌드:** PyInstaller (`--onefile`)

## ⚠️ 제약 사항 및 의존성
- **환경:** Windows 10/11 x64 전용
- **의존성:** Git 2.x (PATH 등록 권장)
- **금지사항:** `requests`, `urllib`, `pickle`, `socket`, `KoNLPy`(JRE 의존), 외부 LLM API/클라우드 통신 일체 금지.

## 📂 문서 색인
상세 설계 및 명세는 [INDEX.md](./docs/INDEX.md)를 참고하시기 바랍니다.
