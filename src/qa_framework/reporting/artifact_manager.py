from __future__ import annotations

import re
from pathlib import Path

from qa_framework.exceptions import ReportingError


def safe_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", nodeid).strip("_")[-180:]


class ArtifactManager:
    def __init__(self, run_dir: Path, max_bytes: int = 1_048_576) -> None:
        self.run_dir = Path(run_dir)
        self.max_bytes = max_bytes
        for name in (
            "logs",
            "reports",
            "screenshots",
            "page_sources",
            "browser_logs",
            "api_exchanges",
            "postman",
        ):
            (self.run_dir / name).mkdir(parents=True, exist_ok=True)

    def write_text(self, category: str, filename: str, content: str) -> Path:
        encoded = content.encode("utf-8", errors="replace")[: self.max_bytes]
        path = self.run_dir / category / filename
        try:
            path.write_bytes(encoded)
        except OSError as exc:
            raise ReportingError(f"cannot write artifact {path}") from exc
        return path

    def capture_webdriver_failure(self, nodeid: str, driver) -> list[Path]:
        name = safe_name(nodeid)
        paths = []
        try:
            screenshot = self.run_dir / "screenshots" / f"{name}.png"
            if driver.save_screenshot(str(screenshot)):
                paths.append(screenshot)
        except Exception:
            pass
        try:
            paths.append(self.write_text("page_sources", f"{name}.html", driver.page_source))
        except Exception:
            pass
        return paths
