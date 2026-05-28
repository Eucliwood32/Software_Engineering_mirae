"""
STAGE 0 - L0 정적 게이트: MVC 단방향 의존 검사 (C-4, architecture 불변식)
소스가 비어도 통과(위반 0건). 디렉토리 없으면 검사 대상 0개 → 통과.
"""
import ast
import pathlib


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


def test_view_does_not_import_model():
    """C-4: View → Model 직접 import 0건."""
    offenders = []
    view_dir = pathlib.Path("qce/view")
    if not view_dir.exists():
        return
    for f in view_dir.rglob("*.py"):
        for _top, full in _imports(f):
            if full.startswith("qce.model"):
                offenders.append((str(f), full))
    assert not offenders, f"View가 Model을 직접 import(C-4 위반): {offenders}"


def test_model_does_not_import_pyqt():
    """architecture 불변식: Model 레이어에 PyQt6·PySide6 import 금지."""
    offenders = []
    model_dir = pathlib.Path("qce/model")
    if not model_dir.exists():
        return
    for f in model_dir.rglob("*.py"):
        for top, _ in _imports(f):
            if top in {"PyQt6", "PySide6"}:
                offenders.append(str(f))
    assert not offenders, f"Model이 UI 프레임워크 import(architecture 불변식 위반): {offenders}"


def test_parsers_do_not_cross_import():
    """NFR-3.2: document_parser·git_analyzer·messenger_parser 상호 import 금지."""
    parsers = {"git_analyzer", "document_parser", "messenger_parser"}
    offenders = []
    base = pathlib.Path("qce/model/parsing")
    for name in parsers:
        f = base / f"{name}.py"
        if not f.exists():
            continue
        for _, full in _imports(f):
            others = parsers - {name}
            if any(o in full for o in others):
                offenders.append((name, full))
    assert not offenders, f"파서 상호 import(NFR-3.2 위반): {offenders}"
