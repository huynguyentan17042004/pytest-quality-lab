from __future__ import annotations

import time
from pathlib import Path

from qa_framework.exceptions import WaitConditionError


class DownloadManager:
    def __init__(self, directory: Path, timeout: float = 10.0, poll: float = 0.1) -> None:
        self.directory = Path(directory)
        self.timeout = timeout
        self.poll = poll

    def wait_for(self, filename: str) -> Path:
        target = self.directory / filename
        deadline = time.monotonic() + self.timeout
        previous_size = -1
        stable_checks = 0
        while time.monotonic() < deadline:
            partials = list(self.directory.glob(f"{filename}*.crdownload")) + list(
                self.directory.glob(f"{filename}*.part")
            )
            if target.is_file() and not partials:
                size = target.stat().st_size
                stable_checks = stable_checks + 1 if size == previous_size else 0
                if stable_checks >= 2:
                    return target
                previous_size = size
            time.sleep(self.poll)
        raise WaitConditionError(f"download did not stabilize before timeout: {target}")
