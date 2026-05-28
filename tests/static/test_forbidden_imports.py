"""
STAGE 0 - L0 정적 게이트: 금지 import 검사 (C-2, C-8, NFR-2.2, NFR-2.3)
소스가 비어도 통과(위반 0건). qce/가 없으면 검사 대상 0개 → 통과.
"""
import ast
import pathlib

FORBIDDEN = {"requests", "urllib", "httpx", "socket", "http.client", "pickle"}
SRC = pathlib.Path("qce")


def _imports(pyfile: pathlib.Path):
    try:
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                yield a.name.split(".")[0], a.name
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            yield mod.split(".")[0], mod


def test_no_forbidden_imports():
    """C-2/C-8: requests·urllib·httpx·socket·http.client·pickle 금지."""
    bad = []
    if not SRC.exists():
        return
    for f in SRC.rglob("*.py"):
        for top, full in _imports(f):
            if top in FORBIDDEN or full in FORBIDDEN:
                bad.append((str(f), full))
    assert not bad, f"금지 import 발견(C-2/C-8): {bad}"


def test_no_jre_dependency():
    """C-7: konlpy·jpype·jpype1 의존 금지 (JRE 불필요)."""
    bad = []
    if not SRC.exists():
        return
    for f in SRC.rglob("*.py"):
        for _, full in _imports(f):
            if full.split(".")[0] in {"konlpy", "jpype", "jpype1"}:
                bad.append((str(f), full))
    assert not bad, f"JRE 의존 형태소 분석기 발견(C-7): {bad}"


def test_no_jre_in_requirements():
    """C-7: requirements.txt / pyproject.toml 에 konlpy·jpype1 없음."""
    bad_lines = []
    for req_file in ["requirements.txt", "pyproject.toml"]:
        p = pathlib.Path(req_file)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            lower = line.strip().lower()
            if any(kw in lower for kw in ("konlpy", "jpype1", "jpype")):
                bad_lines.append(f"{req_file}: {line.strip()}")
    assert not bad_lines, f"JRE 의존 패키지가 의존성 파일에 포함됨(C-7): {bad_lines}"
