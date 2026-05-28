"""
STAGE 0 - L0 정적 게이트: JRE / KoNLPy 의존 추가 검사 (C-7)
test_forbidden_imports.py와 협력하여 이중으로 차단한다.
"""
import ast
import pathlib


def _module_names(pyfile: pathlib.Path):
    try:
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                yield a.name.split(".")[0]
        elif isinstance(n, ast.ImportFrom):
            yield (n.module or "").split(".")[0]


JRE_PACKAGES = {"konlpy", "jpype", "jpype1"}


def test_no_konlpy_in_source():
    """C-7: 소스 전체에서 konlpy·jpype·jpype1 import 0건."""
    bad = []
    src = pathlib.Path("qce")
    if not src.exists():
        return
    for f in src.rglob("*.py"):
        for name in _module_names(f):
            if name in JRE_PACKAGES:
                bad.append((str(f), name))
    assert not bad, f"KoNLPy/JRE 패키지 import(C-7): {bad}"


def test_no_pickle_anywhere():
    """NFR-2.3: 소스 전체에서 pickle import 0건 (캐시는 json만 허용)."""
    bad = []
    src = pathlib.Path("qce")
    if not src.exists():
        return
    for f in src.rglob("*.py"):
        for name in _module_names(f):
            if name == "pickle":
                bad.append(str(f))
    assert not bad, f"pickle import 발견(NFR-2.3 위반): {bad}"
