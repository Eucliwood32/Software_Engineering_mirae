"""FR-2.1 GitAnalyzer: git log --numstat 파싱 → CommitStats."""
from __future__ import annotations
import subprocess
from qce.model.types import CommitStats


class GitAnalyzer:
    GIT_TIMEOUT: int = 30

    def analyze(self, repo_path: str) -> dict[str, CommitStats]:
        """{author_email: CommitStats}. 잘못된 경로/실패 → {} 반환."""
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "log",
                 "--numstat", "--format=%H|%ae|%ai", "--no-merges"],
                capture_output=True, text=True,
                timeout=self.GIT_TIMEOUT, check=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                FileNotFoundError, OSError):
            return {}

        return self._parse_output(result.stdout)

    def _parse_output(self, output: str) -> dict[str, CommitStats]:
        """git log --numstat 출력 파싱. 작성자별 합계와 함께 커밋 단위 명세
        (commits_list = [{hash, date, additions, deletions}, ...])를 보존한다.
        commits_list는 FR-4.2(커밋별 Capping)·FR-4.2b(빈도 신호)·타임라인 차트의 근거다.
        """
        # 가변 누적용 구조(마지막에 CommitStats로 동결).
        agg: dict[str, dict] = {}
        current_email: str | None = None
        current_commit: dict | None = None

        for line in output.splitlines():
            line = line.strip()
            if "|" in line and len(line.split("|")) == 3:
                commit_hash, email, date = (p.strip() for p in line.split("|", 2))
                current_email = email
                bucket = agg.setdefault(
                    email,
                    {"commits": 0, "additions": 0, "deletions": 0, "commits_list": []},
                )
                bucket["commits"] += 1
                current_commit = {
                    "hash": commit_hash,
                    "date": date,
                    "additions": 0,
                    "deletions": 0,
                }
                bucket["commits_list"].append(current_commit)
            elif current_email and current_commit is not None and line and line[0].isdigit():
                parts = line.split("\t")
                if len(parts) >= 2:
                    try:
                        add = int(parts[0]) if parts[0] != "-" else 0
                        delete = int(parts[1]) if parts[1] != "-" else 0
                    except ValueError:
                        continue
                    bucket = agg[current_email]
                    bucket["additions"] += add
                    bucket["deletions"] += delete
                    current_commit["additions"] += add
                    current_commit["deletions"] += delete

        return {
            email: CommitStats(
                b["commits"], b["additions"], b["deletions"], b["commits_list"]
            )
            for email, b in agg.items()
        }
