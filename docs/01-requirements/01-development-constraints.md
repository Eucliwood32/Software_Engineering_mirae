# 개발 제약사항 (Development Constraints)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v2.0 |
| 작성일 | 2026-05-27 |
| 기준 명세 | SRS v2.0 INVEST 개정본 |
| 상위 문서 | SRS v2.0 (통합 명세서), Concept of Operations (ConOps) |
| 작성 주체 | QCE 개발팀 (20222047 조원희 · 20247142 이대한 · 20221985 김휘중) |

---

## 1. 문서 개요
본 문서는 QCE 시스템의 설계, 구현, 배포 전반에 걸쳐 절대적으로 준수해야 하는 **기술적·환경적 제약사항(Constraints)**을 정의합니다. 본 문서에 명시된 제약은 기능적/비기능적 요구사항을 구현할 때 타협할 수 없는 물리적, 구조적 한계를 의미합니다.

---

## 2. 시스템 및 개발 제약사항 (Constraints)

| ID | 제약(Constraint) 명칭 | 상세 내용 및 준수 근거 |
| :--- | :--- | :--- |
| **C-1** | **로컬 자원 단독 사용**<br>(Local CPU/RAM Only) | 어떠한 형태의 클라우드 연산 가속도 지원하지 않으며, 오직 조장(사용자) PC의 로컬 CPU와 RAM만으로 구동되어야 합니다. (완전 로컬 원칙 O-4) |
| **C-2** | **외부 LLM / API 사용 금지**<br>(No External Network) | 데이터 유출을 원천 차단하기 위해 OpenAI API 등 외부 통신을 요구하는 모든 기능과 통신 라이브러리(`requests`, `urllib`, `socket` 등)의 코어 로직 내 `import`를 전면 금지합니다. |
| **C-3** | **에이전트 설치 금지**<br>(No Agent Installation) | 데이터를 수집하기 위해 타 팀원의 PC에 백그라운드 에이전트 등을 설치하는 구조를 배제합니다. QCE는 오직 사용자가 수동으로 적재한 파일만을 읽어 분석합니다. |
| **C-4** | **엄격한 MVC 아키텍처**<br>(Strict MVC Compliance) | 아키텍처 설계 시 **View → Controller → Model**의 단방향 흐름을 강제합니다. View 계층에서 Model을 직접 `import`하거나 호출하는 것을 엄격히 금지합니다. (ADR-0001) |
| **C-5** | **Python 스택 및 Target OS**<br>(Environment Constraints) | 개발 언어는 **Python 3.10 이상**을 기준으로 하며, 대상 운영체제는 **Windows 10/11 x64** 환경으로만 한정합니다. (다중 OS 지원을 위한 분기문 작성 지양) |
| **C-6** | **단일 실행 파일 배포**<br>(Standalone Executable) | 사용자 PC에 별도의 Python 환경이나 라이브러리 설치를 요구하지 않도록, 반드시 `PyInstaller --onefile` 옵션을 활용하여 단일 `.exe` 파일 형태로 빌드 및 배포해야 합니다. |
| **C-7** | **외부 JRE 의존성 배제**<br>(No Java Dependency) | 사용자의 사전 환경 구축 부담을 줄이기 위해, 형태소 분석 시 Java 런타임(JRE)을 요구하는 `KoNLPy`(`Kkma`, `Hannanum` 등)의 사용을 전면 금지합니다. 순수 Python 또는 C 확장 기반의 `kiwipiepy`나 `soynlp`만을 사용해야 합니다. |
| **C-8** | **직렬화 포맷 제한**<br>(No Pickle allowed) | 임의 코드 실행(RCE) 등의 보안 취약점을 방지하기 위해 파일/캐시 직렬화 시 `pickle` 모듈의 사용을 전면 금지합니다. 모든 데이터 직렬화는 `json` 모듈만 사용해야 합니다. |
| **C-9** | **Git CLI 의존성 대응**<br>(Git CLI Prerequisite) | Git 로컬 저장소 분석을 위해 사용자 OS에 `Git 2.x` CLI가 설치되고 PATH에 등록되어 있어야 합니다. 단, 미설치 환경에서도 앱이 비정상 종료(Crash)되지 않고 기능을 우회할 수 있도록 에러 핸들링이 강제됩니다. |