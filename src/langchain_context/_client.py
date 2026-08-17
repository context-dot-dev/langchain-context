from __future__ import annotations

import base64
import binascii
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import SecretStr

from langchain_context._spec import EndpointParameter, EndpointSpec

JsonObject = dict[str, Any]
DEFAULT_API_BASE = "https://api.context.dev/v1"
DEFAULT_TIMEOUT_SECONDS = 180.0
OMITTED_RESPONSE_FIELDS = {"debug", "key_metadata", "request_id", "trace_id"}


class ContextError(RuntimeError):
    """Base error raised by the Context.dev integration."""


class ContextConfigurationError(ContextError):
    """Raised when the client is missing required configuration."""


class ContextConnectionError(ContextError):
    """Raised when the Context API cannot be reached."""


class ContextAPIError(ContextError):
    """Raised when the Context API returns an unsuccessful response."""

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        error_code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        code_suffix = f" [{error_code}]" if error_code else ""
        request_suffix = f" (request {request_id})" if request_id else ""
        super().__init__(f"Context API {status_code}{code_suffix}: {message}{request_suffix}")
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id


def resolve_api_key(value: SecretStr | str | None = None) -> SecretStr:
    if isinstance(value, SecretStr) and value.get_secret_value().strip():
        return value
    if isinstance(value, str) and value.strip():
        return SecretStr(value.strip())
    environment_value = os.getenv("CONTEXT_API_KEY", "").strip()
    if environment_value:
        return SecretStr(environment_value)
    raise ContextConfigurationError("Context API key missing. Pass api_key or set CONTEXT_API_KEY.")


def resolve_api_base(value: str | None = None) -> str:
    base_url = (value or os.getenv("CONTEXT_API_BASE") or DEFAULT_API_BASE).strip()
    if not base_url.startswith(("http://", "https://")):
        raise ContextConfigurationError("Context API base must be an HTTP(S) URL.")
    return base_url.rstrip("/")


def _query_values(name: str, value: Any) -> list[tuple[str, str]]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [pair for item in value for pair in _query_values(name, item)]
    if isinstance(value, dict):
        return [
            pair for key, item in value.items() for pair in _query_values(f"{name}[{key}]", item)
        ]
    if isinstance(value, bool):
        return [(name, "true" if value else "false")]
    return [(name, str(value))]


def _parameter_values(
    endpoint: EndpointSpec,
    arguments: JsonObject,
    location: str,
) -> list[tuple[EndpointParameter, Any]]:
    return [
        (parameter, arguments.get(parameter.name))
        for parameter in endpoint.parameters
        if parameter.location == location and arguments.get(parameter.name) is not None
    ]


def _request_body(endpoint: EndpointSpec, arguments: JsonObject) -> Any:
    if "body" in arguments:
        return arguments["body"]
    parameter_names = {parameter.name for parameter in endpoint.parameters}
    return {
        name: value
        for name, value in arguments.items()
        if value is not None and name != "fileBase64" and name not in parameter_names
    }


def _binary_body(arguments: JsonObject) -> bytes:
    encoded = arguments.get("fileBase64")
    if not isinstance(encoded, str) or not encoded:
        raise ValueError("fileBase64 is required for document parsing.")
    try:
        return base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("fileBase64 must be valid base64-encoded bytes.") from exc


def _path(endpoint: EndpointSpec, arguments: JsonObject) -> str:
    result = endpoint.path
    for parameter, value in _parameter_values(endpoint, arguments, "path"):
        result = result.replace(f"{{{parameter.name}}}", quote(str(value), safe=""))
    return result


def _validation_message(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    messages: list[str] = []
    for issue in value:
        if not isinstance(issue, dict) or not isinstance(issue.get("message"), str):
            continue
        path = issue.get("path")
        location = ".".join(str(part) for part in path) if isinstance(path, list) else "input"
        messages.append(f"{location}: {issue['message']}")
    return "; ".join(messages) or None


def _response_value(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if response.is_error:
        record = payload if isinstance(payload, dict) else {}
        message = next(
            (
                record[key]
                for key in ("message", "error", "error_description")
                if isinstance(record.get(key), str) and record[key]
            ),
            _validation_message(record.get("message")) or response.text.strip() or "Request failed",
        )
        raise ContextAPIError(
            status_code=response.status_code,
            message=message,
            error_code=(
                record.get("error_code") if isinstance(record.get("error_code"), str) else None
            ),
            request_id=(
                record.get("request_id") if isinstance(record.get("request_id"), str) else None
            ),
        )
    if isinstance(payload, dict):
        return {
            name: value for name, value in payload.items() if name not in OMITTED_RESPONSE_FIELDS
        }
    return payload if payload is not None else response.text


@dataclass(frozen=True)
class ContextClient:
    """HTTP client for the public Context.dev API."""

    api_key: SecretStr
    api_base: str = DEFAULT_API_BASE
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    sync_client: httpx.Client | None = None
    async_client: httpx.AsyncClient | None = None

    @classmethod
    def create(
        cls,
        *,
        api_key: SecretStr | str | None = None,
        api_base: str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        sync_client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ) -> ContextClient:
        return cls(
            api_key=resolve_api_key(api_key),
            api_base=resolve_api_base(api_base),
            timeout=timeout,
            sync_client=sync_client,
            async_client=async_client,
        )

    def _request_parts(
        self,
        endpoint: EndpointSpec,
        arguments: JsonObject,
    ) -> tuple[str, list[tuple[str, str]], dict[str, str], Any, bytes | None]:
        params = [
            pair
            for parameter, value in _parameter_values(endpoint, arguments, "query")
            for pair in _query_values(parameter.name, value)
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "User-Agent": "langchain-context/0.1.0",
        }
        headers.update(
            {
                parameter.name: str(value)
                for parameter, value in _parameter_values(endpoint, arguments, "header")
            }
        )
        json_body: Any = None
        content: bytes | None = None
        if endpoint.request_body is not None:
            if endpoint.request_body.binary:
                content = _binary_body(arguments)
                headers["Content-Type"] = (
                    "application/octet-stream"
                    if endpoint.request_body.content_type == "*/*"
                    else endpoint.request_body.content_type
                )
            else:
                json_body = _request_body(endpoint, arguments)
        return _path(endpoint, arguments), params, headers, json_body, content

    def request(self, endpoint: EndpointSpec, arguments: JsonObject) -> Any:
        path, params, headers, json_body, content = self._request_parts(endpoint, arguments)
        request_kwargs: dict[str, Any] = {
            "method": endpoint.method,
            "url": f"{self.api_base}{path}",
            "params": params,
            "headers": headers,
        }
        if endpoint.request_body is not None:
            request_kwargs["content" if endpoint.request_body.binary else "json"] = (
                content if endpoint.request_body.binary else json_body
            )
        try:
            if self.sync_client is not None:
                response = self.sync_client.request(**request_kwargs)
            else:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(**request_kwargs)
        except httpx.HTTPError as exc:
            raise ContextConnectionError(f"Failed to reach Context API: {exc}") from exc
        return _response_value(response)

    async def arequest(self, endpoint: EndpointSpec, arguments: JsonObject) -> Any:
        path, params, headers, json_body, content = self._request_parts(endpoint, arguments)
        request_kwargs: dict[str, Any] = {
            "method": endpoint.method,
            "url": f"{self.api_base}{path}",
            "params": params,
            "headers": headers,
        }
        if endpoint.request_body is not None:
            request_kwargs["content" if endpoint.request_body.binary else "json"] = (
                content if endpoint.request_body.binary else json_body
            )
        try:
            if self.async_client is not None:
                response = await self.async_client.request(**request_kwargs)
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(**request_kwargs)
        except httpx.HTTPError as exc:
            raise ContextConnectionError(f"Failed to reach Context API: {exc}") from exc
        return _response_value(response)
