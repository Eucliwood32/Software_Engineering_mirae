import os
import re
import typing

def parse_messenger_file(file_path: str) -> typing.Dict[str, typing.Any]:
    """
    FR-3.1, 3.2: 카카오톡 내보내기 파싱, 방어적 예외 처리 (Slack 기능 제외됨)
    """
    if not os.path.exists(file_path):
        return {"error": "file_not_found", "path": file_path}
        
    # NFR-3.1: 인코딩 자동 감지
    encodings = ['utf-8', 'cp949']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return _parse_kakao_txt(f)
        except UnicodeDecodeError:
            continue
            
    return {"error": "encoding_failed", "path": file_path}

def _parse_kakao_txt(file_obj) -> typing.Dict[str, typing.Any]:
    records = []
    skipped = 0
    
    date_pattern = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일")
    msg_pattern = re.compile(r"^(.+?)\s:\s(.+)$")
    
    for line in file_obj:
        line = line.strip()
        if not line:
            continue
            
        try:
            if date_pattern.match(line):
                continue
                
            match = msg_pattern.match(line)
            if match:
                records.append({
                    "author": match.group(1).strip(),
                    "timestamp": "",
                    "message": match.group(2).strip()
                })
            else:
                skipped += 1
        except Exception:
            skipped += 1
            
    return {"records": records, "skipped_lines": skipped}
