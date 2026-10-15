from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .context import log_context
from .redaction import Redactor


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            **(log_context.get() or {}),
        }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(directory: Path, secrets: tuple[str, ...] = ()) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("qa_framework")
    logger.setLevel(logging.DEBUG)
    if any(getattr(handler, "_qa_handler", False) for handler in logger.handlers):
        return
    redactor = Redactor(secrets)
    for name, formatter in (
        ("run.log", logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")),
        ("run.jsonl", JsonLineFormatter()),
    ):
        handler = logging.FileHandler(directory / name, encoding="utf-8")
        handler._qa_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(formatter)
        handler.addFilter(redactor)
        logger.addHandler(handler)
