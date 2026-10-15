from __future__ import annotations

from contextvars import ContextVar

log_context: ContextVar[dict[str, str] | None] = ContextVar("qa_log_context", default=None)


def bind_context(**values: str) -> None:
    log_context.set({**(log_context.get() or {}), **values})


def clear_context() -> None:
    log_context.set({})
