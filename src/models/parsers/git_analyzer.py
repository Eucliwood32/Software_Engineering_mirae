"""FR-2.1 GitAnalyzer: git log --numstat 파싱 → CommitStats + commits_list."""
from __future__ import annotations
import subprocess
import sys
from src.models.types import CommitStats


class GitAnalyzer:
    """FR-2.1 — git log 수집. 잘못된 경로/실패 → {} 반환(예외 비전파).

    commits_list 필드는 AnomalySignalDetector(FR-4.2b)가 일자별 시계열 분석에 사용한다.
    """

    GIT_TIMEOUT: int = 30

    def analyze(self, repo_path: str) -> dict[str, CommitStats]:
        """{author_email: CommitStats}. 실패 시 빈 dict."""
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "log",
                 "--numstat", "--format=%H|%ae|%ai", "--no-merges"],
                capture_output=True,
                text=True,
                timeout=self.GIT_TIMEOUT,
                check=True,
                stdin=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                FileNotFoundError, OSError):
            return {}

        return self._parse_output(result.stdout)

    def _parse_output(self, output: str) -> dict[str, CommitStats]:
        stats: dict[str, CommitStats] = {}
        current_email: str | None = None
        current_hash: str | None = None
        current_date: str | None = None

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            if "|" in line and len(line.split("|")) == 3:
                current_hash, current_email, current_date = (
                    p.strip() for p in line.split("|", 2)
                )
                if current_email not in stats:
                    stats[current_email] = CommitStats(0, 0, 0, [])
                prev = stats[current_email]
                stats[current_email] = CommitStats(
                    prev.commits + 1,
                    prev.additions,
                    prev.deletions,
                    prev.commits_list,
                )
                stats[current_email].commits_list.append({
                    "hash": current_hash,
                    "date": current_date,
                    "additions": 0,
                    "deletions": 0,
                })

            elif current_email and line and line[0].isdigit():
                parts = line.split("\t")
                if len(parts) >= 2:
                    try:
                        add = int(parts[0]) if parts[0] != "-" else 0
                        delete = int(parts[1]) if parts[1] != "-" else 0
                        s = stats[current_email]
                        stats[current_email] = CommitStats(
                            s.commits,
                            s.additions + add,
                            s.deletions + delete,
                            s.commits_list,
                        )
                        if s.commits_list:
                            last = s.commits_list[-1]
                            last["additions"] += add
                            last["deletions"] += delete
                    except ValueError:
                        pass

        return stats
