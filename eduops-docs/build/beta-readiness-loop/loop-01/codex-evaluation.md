CODEX_DECISION: IMPROVE

읽기 전용 평가를 시도했지만, 현재 실행 환경에서 모든 파일 읽기 명령이 `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`로 실패했습니다. MCP 리소스도 비어 있어 HISYS EduOps 통제 문서를 실제로 열람할 수 없었습니다.

따라서 “베타 테스터가 사용할 수 있는 제품 개발을 지금 시작해도 충분하다”고 승인할 근거가 없습니다.

우선 보완/확인 필요 항목:

1. 통제 문서 접근성 확보
   - HISYS EduOps PRD, 기능 명세, 아키텍처, UX 플로우, 데이터 모델, 테스트 게이트 문서를 평가자가 읽을 수 있어야 합니다.

2. 베타 착수 기준 명시
   - Windows desktop-first/local-first 범위
   - 베타 테스터가 실제 수행할 핵심 시나리오
   - MVP와 베타 제외 범위
   - 수용 기준과 중단 기준

3. Git-backed Notion-style assignments 명세
   - 과제/페이지/블록 모델
   - Git 저장 구조
   - 충돌 처리
   - 오프라인 편집 및 동기화 규칙

4. fake/local fixture gate 정의
   - 라이브 액션 전 반드시 통과해야 하는 로컬 fixture
   - GitHub 연동 전 시뮬레이션 경로
   - 테스트 데이터와 실패 케이스

5. No LMS 경계 명확화
   - LMS 미지원 범위
   - 가져오기/내보내기 정책
   - 베타에서 혼동될 수 있는 LMS 유사 기능 제외 기준

6. GitHub-first later 전환 계획
   - 로컬 Git 우선 구조가 이후 GitHub 연동으로 확장되는 방식
   - 인증, 권한, 원격 저장소, PR/issue 연계의 후속 단계

현재 상태는 문서 충분성 자체를 검증할 수 없으므로 `IMPROVE`입니다.
