from __future__ import annotations

import os
import re
from collections.abc import Mapping
from typing import Any

from qa_framework.config import SecretValue
from qa_framework.exceptions import MissingVariableError

PLACEHOLDER = re.compile(r"^\$\{([A-Z][A-Z0-9_]*)\}$")


def resolve_runtime_variables(value: Any, environ: Mapping[str, str] | None = None) -> Any:
    source = os.environ if environ is None else environ
    if isinstance(value, dict):
        return {key: resolve_runtime_variables(item, source) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_runtime_variables(item, source) for item in value]
    if isinstance(value, str) and (match := PLACEHOLDER.fullmatch(value)):
        name = match.group(1)
        if not source.get(name):
            raise MissingVariableError(f"required runtime variable {name} is missing")
        return SecretValue(source[name])
    return value
