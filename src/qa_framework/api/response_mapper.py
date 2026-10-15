from __future__ import annotations

from qa_framework.api.api_response import ApiResponse
from qa_framework.exceptions import ResponseParseError


class ResponseMapper:
    @staticmethod
    def map(response) -> ApiResponse:
        body = None
        if response.status_code != 204 and response.content:
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type:
                try:
                    body = response.json()
                except ValueError as exc:
                    raise ResponseParseError(
                        "response declared JSON but could not be parsed"
                    ) from exc
            else:
                body = response.text
        return ApiResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            elapsed_seconds=response.elapsed.total_seconds(),
            body=body,
            raw=response,
        )
