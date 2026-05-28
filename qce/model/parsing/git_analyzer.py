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
        stats: dict[str, CommitStats] = {}
        current_email: str | None = None

        for line in output.splitlines():
            line = line.strip()
            if "|" in line and len(line.split("|")) == 3:
                _, email, _ = line.split("|", 2)
                current_email = email.strip()
                if current_email not in stats:
                    stats[current_email] = CommitStats(0, 0, 0)
                stats[current_email] = CommitStats(
                    stats[current_email].commits + 1,
                    stats[current_email].additions,
                    stats[current_email].deletions,
                )
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
                        )
                    except ValueError:
                        pass

        return stats
