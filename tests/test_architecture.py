import os
import ast
import pytest

def test_no_network_and_pickle_imports():
    """
    NFR-2.2 (네트워크 통신 배제) 및 C-8 (Pickle 금지) 정적 분석 검증
    """
    banned_modules = {'requests', 'urllib', 'socket', 'httpx', 'http.client', 'pickle'}
    
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            assert alias.name not in banned_modules, f"Banned module {alias.name} imported in {file}"
                    elif isinstance(node, ast.ImportFrom):
                        assert node.module not in banned_modules, f"Banned module {node.module} imported in {file}"

def test_no_jre_dependency():
    """
    C-7 (JRE 배제) 정적 분석 검증 - KoNLPy 사용 금지
    """
    banned_modules = {'konlpy', 'jpype'}
    
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            assert alias.name not in banned_modules, f"JRE dependent module {alias.name} imported in {file}"
                    elif isinstance(node, ast.ImportFrom):
                        assert node.module not in banned_modules, f"JRE dependent module {node.module} imported in {file}"
