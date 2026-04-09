from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

import allure
import requests


def _serialize_headers(headers: Any) -> str:
    return json.dumps(dict(headers), indent=2, sort_keys=True)


def _serialize_body(body: Any) -> str:
    if body is None:
        return ""
    if isinstance(body, bytes):
        return body.decode("utf-8", errors="replace")
    if isinstance(body, str):
        return body
    return json.dumps(body, indent=2, sort_keys=True)


def attach_http_exchange(response: requests.Response) -> None:
    request = response.request
    request_lines = [
        f"{request.method} {request.url}",
        "",
        _serialize_headers(request.headers),
        "",
        _serialize_body(request.body),
    ]
    response_body = response.text
    try:
        response_body = json.dumps(response.json(), indent=2, sort_keys=True)
    except ValueError:
        pass

    response_lines = [
        f"HTTP {response.status_code}",
        "",
        _serialize_headers(response.headers),
        "",
        response_body,
    ]

    allure.attach(
        "\n".join(request_lines).strip(),
        name="http-request",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        "\n".join(response_lines).strip(),
        name="http-response",
        attachment_type=allure.attachment_type.TEXT,
    )


class AllureLoggingSession(requests.Session):
    def __init__(self, *, default_headers: dict[str, str] | None = None) -> None:
        super().__init__()
        self.headers.update(default_headers or {})
        self.hooks["response"].append(self._allure_hook)

    def _allure_hook(self, response: requests.Response, *args: Any, **kwargs: Any) -> requests.Response:
        attach_http_exchange(response)
        return response


def build_default_headers(correlation_id: str | None = None) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id or str(uuid4()),
    }
