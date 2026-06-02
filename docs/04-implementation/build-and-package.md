# 빌드 및 패키징 (Build & Package)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-05-31 |
| 대상 제약 | C-6 (단일 실행 파일), C-5 (Python 스택·Windows) |
| 빌드 도구 | PyInstaller 6.12.0, Python 3.12 |

---

## 1. 개요

QCE는 PyInstaller `--onefile` 모드로 **의존성이 포함된 단일 실행 파일**(`QCE.exe`)로 패키징된다(C-6). 엔트리포인트는 `main.py`이며, 정본 코드베이스 `qce/` 패키지(MVC)를 번들한다. 레거시 경로(`src/`, `BusinessLogic/`)는 `main.py`가 import하지 않으므로 번들에 포함되지 않는다.

---

## 2. 빌드 산출물

| 산출물 | spec | 콘솔 | 용도 |
| :--- | :--- | :--- | :--- |
| `dist/QCE.exe` | `QCE.spec` | 없음(`--windowed`) | **배포용** 최종 실행 파일 |
| `dist/QCE_debug.exe` | `QCE_debug.spec` | 있음(`console=True`) | 디버그용. 起動 로그·예외를 콘솔에 출력 |

> `.spec` 파일은 빌드 레시피이므로 **버전 관리에 포함**한다. `build/`·`dist/` 산출물은 `.gitignore`로 제외한다.

---

## 3. 재현 빌드 명령

```powershell
# 배포용 (windowed)
python -m PyInstaller QCE.spec --clean --noconfirm

# 디버그용 (console — 起動 오류 진단 시)
python -m PyInstaller QCE_debug.spec --clean --noconfirm
```

산출물은 `dist/QCE.exe` 에 생성된다.

---

## 4. 핵심 번들 설정 (spec)

`main.py`의 정적 import만으로는 누락되는 동적 의존성을 다음과 같이 보강한다.

| 항목 | 처리 | 이유 |
| :--- | :--- | :--- |
| `qce` 패키지 | `collect_all('qce')` | 일부 모듈이 함수 내부에서 지연 import됨(예: `SaveReportDialog`) |
| `numpy` | `collect_all('numpy')` + `numpy._core._exceptions`/`_methods`/`_dtype_ctypes`/`_internal` hidden import | **NumPy 2.x C-확장**이 PyInstaller 정적 분석에서 누락되어 `ModuleNotFoundError: numpy._core._exceptions` 발생 → 명시 보강 필수 |
| `matplotlib` | `collect_data_files('matplotlib')` | 차트 렌더링용 데이터(폰트·스타일) 포함 |
| `charset_normalizer` | hidden import | 인코딩 자동 감지(NFR-3.1)에서 동적 로드 |

> **NumPy 2.x 주의.** numpy 보정이 누락되면 起動 즉시 `numpy._core` import 실패로 크래시한다. 두 spec 모두 이 보정을 포함해야 한다.

---

## 5. 빌드 검증

1. **콘솔 빌드 起動 확인**: `dist/QCE_debug.exe` 실행 → 콘솔에 numpy/import 오류 없이 메인 윈도우가 뜨면 번들 정합성 OK.
2. **배포 빌드 起動 확인**: `dist/QCE.exe` 실행 → SubmitScreen 표시(파일 드롭·Git 선택·가중치 패널).
3. 起動 실패 시 `QCE_debug.exe`의 콘솔 출력으로 누락 모듈을 확인하고, 해당 모듈을 `hiddenimports` 또는 `collect_all`로 보강 후 재빌드한다.

---

## 6. 문서 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-05-31 | 최초 작성. PyInstaller --onefile 빌드 절차, NumPy 2.x C-확장 보정, 배포/디버그 2종 산출물, 재현 명령·검증 절차 기록. | QCE 개발팀 |
| **v1.1** | **2026-06-02** | **전역 문서 업데이트의 일환 (Capping 한도 상향 및 UI/UX 디자인 개선 변경사항 동기화).** | 이대한, 김휘중 공동 작업 |
