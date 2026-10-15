from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_KEYS = re.compile(r"(?i)(authorization|token|password|secret|api[_-]?key|cookie)")


def environment_secrets(environment: Mapping[str, str]) -> tuple[str, ...]:
    """Return useful secret values without treating tiny values as global substrings."""
    values = {
        value
        for key, value in environment.items()
        if SENSITIVE_KEYS.search(key) and value and len(value) >= 4
    }
    return tuple(sorted(values, key=len, reverse=True))


def redact(value: Any, secrets: Iterable[str] = ()) -> Any:
    if isinstance(value, dict):
        return {
            key: "********" if SENSITIVE_KEYS.search(str(key)) else redact(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        converted = [redact(item, secrets) for item in value]
        return type(value)(converted)
    text = str(value)
    text = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1********", text)
    text = re.sub(r"(?i)((?:password|token|secret|api[_-]?key)=)[^&\s]+", r"\1********", text)
    for secret in sorted((item for item in secrets if item), key=len, reverse=True):
        text = text.replace(secret, "********")
    return text


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query = [
        (key, "********" if SENSITIVE_KEYS.search(key) else value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


class Redactor(logging.Filter):
    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self.secrets = tuple(secrets)

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage(), self.secrets)
        record.args = ()
        return True
