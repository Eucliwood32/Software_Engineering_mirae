"""
STAGE 0 - L0 정적 게이트: 입력 파일 쓰기 모드 open 탐지 (NFR-2.1)
소스가 비어도 통과(위반 0건). 화이트리스트 모듈은 제외.
"""
import ast
import pathlib

WRITE_MODES = {"w", "a", "x", "w+", "r+", "wb", "ab", "xb"}

# 쓰기가 허용된 모듈 경로 (정규화된 문자열로 비교)
WRITE_OK = {
    str(pathlib.Path("qce/model/business/report_exporter.py")),
    str(pathlib.Path("qce/model/business/cache_manager.py")),
}


def _has_write_open(pyfile: pathlib.Path) -> bool:
    """open(..., 'w'|'a'|'x'|...) 형태의 AST 노드 존재 여부."""
    try:
        tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_open = (
            (isinstance(func, ast.Name) and func.id == "open")
            or (isinstance(func, ast.Attribute) and func.attr == "open")
        )
        if not is_open:
            continue
        # 두 번째 인자(mode)가 문자열 리터럴인 경우만 정적 탐지
        if len(node.args) >= 2:
            mode_arg = node.args[1]
            if isinstance(mode_arg, ast.Constant) and isinstance(mode_arg.value, str):
                if mode_arg.value in WRITE_MODES:
                    return True
        # 키워드 인자 mode=... 형태
        for kw in node.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                if kw.value.value in WRITE_MODES:
                    return True
    return False


def test_analysis_modules_do_not_write_input():
    """NFR-2.1: 분석·파싱 모듈에서 쓰기 모드 open 호출 없음 (화이트리스트 제외)."""
    offenders = []
    src = pathlib.Path("qce")
    if not src.exists():
        return
    for f in src.rglob("*.py"):
        if str(f) in WRITE_OK:
            continue
        if _has_write_open(f):
            offenders.append(str(f))
    assert not offenders, f"분석 경로에 쓰기 open 발견(NFR-2.1 위반): {offenders}"
