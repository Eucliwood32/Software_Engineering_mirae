"""FR-2.2 GitHealthChecker: git 설치·PATH 확인."""
from __future__ import annotations
import subprocess


class GitHealthChecker:
    """FR-2.2 — 메인 윈도우 표시 전 1회 호출. git 미설치 시 False."""

    def is_available(self) -> bool:
        """git --version (timeout 5s). FileNotFoundError 또는 returncode!=0 → False."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False
