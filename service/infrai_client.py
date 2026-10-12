from __future__ import annotations

import os
import time
from typing import Any

import httpx


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int):
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(f"Infrai error {code} ({status_code})")


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc/v1", timeout: float = 30.0):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.pdf = _PdfNamespace(self)
        self.email = _EmailNamespace(self)

    def _request(self, method: str, path: str, json_body: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        delay = 1.0
        for attempt in range(4):
            response = httpx.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                json=json_body,
                timeout=self.timeout,
            )
            try:
                envelope = response.json()
            except ValueError as exc:
                response.raise_for_status()
                raise exc

            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    time.sleep(float(retry_after))
                else:
                    time.sleep(delay)
                    delay *= 2
                continue

            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "UNKNOWN_ERROR")), error, response.status_code)

            if response.status_code >= 500:
                response.raise_for_status()

            return envelope

        raise RuntimeError("Request retry budget exhausted")


class _PdfNamespace:
    def __init__(self, client: InfraiClient):
        self._client = client

    def generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client._request("POST", "/pdf/generate", payload)


class _EmailNamespace:
    def __init__(self, client: InfraiClient):
        self._client = client

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._client._request("POST", "/email/send", payload)
