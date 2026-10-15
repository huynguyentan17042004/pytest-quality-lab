from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urljoin

import requests

from qa_framework.exceptions import ApiTimeoutError, ApiTransportError
from qa_framework.logging.redaction import redact_url

logger = logging.getLogger("qa_framework.api")


class BaseApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        session: Any | None = None,
        timeout: float = 10.0,
        default_headers: Mapping[str, str] | None = None,
        retry_count: int = 0,
        request_budget: int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.session = session or requests.Session()
        self._owns_session = session is None
        self.timeout = timeout
        self.retry_count = retry_count
        self.request_budget = request_budget
        self.attempts = 0
        if default_headers:
            self.session.headers.update(default_headers)

    def request(self, method: str, path: str, **kwargs):
        method = method.upper()
        retries = self.retry_count if method in {"GET", "HEAD", "OPTIONS"} else 0
        url = urljoin(self.base_url, path.lstrip("/"))
        timeout = kwargs.pop("timeout", self.timeout)
        for attempt in range(retries + 1):
            if self.request_budget is not None and self.attempts >= self.request_budget:
                raise ApiTransportError("request budget exceeded before sending request")
            self.attempts += 1
            started = time.monotonic()
            try:
                response = self.session.request(method, url, timeout=timeout, **kwargs)
            except requests.Timeout as exc:
                if attempt < retries:
                    continue
                raise ApiTimeoutError(
                    f"{method} {redact_url(url)} timed out after {timeout}s"
                ) from exc
            except requests.RequestException as exc:
                if attempt < retries:
                    continue
                raise ApiTransportError(f"{method} {redact_url(url)} transport failed") from exc
            duration = time.monotonic() - started
            logger.info(
                "%s %s -> %s in %.3fs", method, redact_url(url), response.status_code, duration
            )
            if response.status_code in {429, 502, 503, 504} and attempt < retries:
                continue
            return response
        raise ApiTransportError("request failed without a response")

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
