import subprocess
import typing
import sys

def parse_git_log(repo_path: str) -> typing.Dict[str, typing.Any]:
    """
    FR-2.1: git log 기반 커밋 데이터 추출
    FR-4.2 등 신호 분석을 위해 개별 커밋 내역(추가/삭제 줄, 날짜)까지 포함하여 반환한다.
    반환 구조:
    {
        "author@email.com": {
            "commits_list": [
                {"hash": "xxx", "date": "2024-01-01", "additions": 10, "deletions": 5}
            ],
            "total_commits": 3,
            "total_additions": 100,
            "total_deletions": 50
        }
    }
    """
    result = {}
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        process = subprocess.run(
            ["git", "log", "--numstat", "--format=%H|%ae|%ai"], 
            cwd=repo_path, 
            capture_output=True, 
            stdin=subprocess.DEVNULL,
            text=True, 
            timeout=30,
            check=True,
            creationflags=creationflags
        )
        
        current_author = None
        current_hash = None
        current_date = None
        
        for line in process.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            
            if "|" in line and len(line.split("|")) >= 3:
                parts = line.split("|")
                current_hash = parts[0].strip()
                current_author = parts[1].strip()
                current_date = parts[2].strip()
                
                if current_author not in result:
                    result[current_author] = {
                        "commits_list": [],
                        "total_commits": 0,
                        "total_additions": 0,
                        "total_deletions": 0
                    }
                result[current_author]["total_commits"] += 1
                result[current_author]["commits_list"].append({
                    "hash": current_hash,
                    "date": current_date,
                    "additions": 0,
                    "deletions": 0
                })
            else:
                if current_author and result[current_author]["commits_list"]:
                    parts = line.split()
                    if len(parts) >= 2:
                        adds = parts[0]
                        dels = parts[1]
                        
                        last_commit = result[current_author]["commits_list"][-1]
                        
                        if adds.isdigit():
                            val = int(adds)
                            last_commit["additions"] += val
                            result[current_author]["total_additions"] += val
                        if dels.isdigit():
                            val = int(dels)
                            last_commit["deletions"] += val
                            result[current_author]["total_deletions"] += val
                            
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {}
        
    return result
