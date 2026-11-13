from __future__ import annotations

import base64
import json
from copy import deepcopy
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from langchain_context import (
    ALL_CONTEXT_TOOL_TYPES,
    ContextAPIError,
    ContextConfigurationError,
    ContextConnectionError,
    ContextGetBatch,
    ContextParse,
    ContextScrape,
    ContextSearch,
    ContextSubmitBatch,
)
from langchain_context._client import ContextClient
from langchain_context._spec import endpoint_registry, endpoint_spec

EXPECTED_ENDPOINTS = {
    "brand-retrieve-unified",
    "cancel-batch",
    "create-monitor",
    "delete-batch",
    "delete-monitor",
    "get-batch",
    "get-batch-results",
    "get-change",
    "get-monitor",
    "get-monitor-run",
    "list-account-runs",
    "list-batches",
    "list-changes",
    "list-monitor-changes",
    "list-monitor-credit-usage",
    "list-monitor-runs",
    "list-monitors",
    "parse-document",
    "run-monitor-now",
    "submit-batch",
    "update-monitor",
    "web-crawl",
    "web-extract",
    "web-fonts",
    "web-naics",
    "web-screenshot",
    "web-scrape-html",
    "web-scrape-images",
    "web-scrape-markdown",
    "web-scrape-sitemap",
    "web-search",
    "web-sic",
    "web-styleguide",
}


def _value_for_schema(schema: dict[str, Any]) -> Any:
    if "default" in schema:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    for choice_name in ("oneOf", "anyOf"):
        choices = schema.get(choice_name)
        if isinstance(choices, list) and choices:
            return _value_for_schema(choices[0])
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((value for value in schema_type if value != "null"), "null")
    if schema_type == "string":
        if schema.get("format") == "uri":
            return "https://example.com"
        return "x" * max(1, schema.get("minLength", 1))
    if schema_type == "integer":
        return schema.get("minimum", 0)
    if schema_type == "number":
        return schema.get("minimum", 0)
    if schema_type == "boolean":
        return False
    if schema_type == "array":
        minimum_items = schema.get("minItems", 0)
        return [_value_for_schema(schema.get("items", {})) for _ in range(minimum_items)]
    if schema_type == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        return {name: _value_for_schema(properties[name]) for name in schema.get("required", [])}
    return None


def _minimal_arguments(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties", {})
    return {
        name: (
            base64.b64encode(b"document").decode("ascii")
            if name == "fileBase64"
            else _value_for_schema(properties[name])
        )
        for name in schema.get("required", [])
    }


def test_public_tool_catalog_is_complete_and_unique() -> None:
    endpoint_names = {tool_type.endpoint_name for tool_type in ALL_CONTEXT_TOOL_TYPES}
    tool_names = {tool_type(api_key="test").name for tool_type in ALL_CONTEXT_TOOL_TYPES}

    assert endpoint_names == EXPECTED_ENDPOINTS
    assert endpoint_names == set(endpoint_registry().endpoints)
    assert len(tool_names) == len(EXPECTED_ENDPOINTS)


@pytest.mark.parametrize("tool_type", ALL_CONTEXT_TOOL_TYPES)
def test_every_tool_exposes_a_resolved_validatable_schema(tool_type: type[Any]) -> None:
    tool = tool_type(api_key="test")
    schema = tool.tool_call_schema

    assert isinstance(schema, dict)
    assert "$ref" not in repr(schema)
    assert schema["additionalProperties"] is False
    assert tool.description
    assert tool.metadata == {
        "context_endpoint": tool.endpoint_name,
        "read_only": endpoint_spec(tool.endpoint_name).annotations.read_only,
        "destructive": endpoint_spec(tool.endpoint_name).annotations.destructive,
        "open_world": endpoint_spec(tool.endpoint_name).annotations.open_world,
    }
    tool.get_input_schema().model_validate(_minimal_arguments(schema))


def test_every_nested_tool_parameter_has_a_description() -> None:
    missing: list[str] = []

    def visit(schema: dict[str, Any], path: str) -> None:
        for name, value in schema.get("properties", {}).items():
            if not value.get("description"):
                missing.append(f"{path}.{name}")
            visit(value, f"{path}.{name}")
            for composition in ("oneOf", "anyOf", "allOf"):
                for index, choice in enumerate(value.get(composition, [])):
                    visit(choice, f"{path}.{name}.{composition}[{index}]")
            if isinstance(value.get("items"), dict):
                visit(value["items"], f"{path}.{name}[]")

    for tool_type in ALL_CONTEXT_TOOL_TYPES:
        tool = tool_type(api_key="test")
        visit(tool.tool_call_schema, tool.endpoint_name)

    assert missing == []


@pytest.mark.parametrize("tool_type", ALL_CONTEXT_TOOL_TYPES)
def test_every_tool_can_build_and_send_its_minimum_request(tool_type: type[Any]) -> None:
    observed_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"ok": True})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    tool = tool_type(context_client=client)

    assert tool.invoke(_minimal_arguments(tool.tool_call_schema)) == {"ok": True}
    assert observed_request is not None
    assert "{" not in observed_request.url.path


def test_sync_tool_invocation_builds_json_request() -> None:
    observed_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"results": [{"title": "Context.dev"}]})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1/",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    arguments = {
        "query": "Context.dev",
        "numResults": 10,
        "includeDomains": ["context.dev"],
    }
    original_arguments = deepcopy(arguments)

    result = ContextSearch(context_client=client).invoke(arguments)

    assert result == {"results": [{"title": "Context.dev"}]}
    assert observed_request is not None
    assert observed_request.method == "POST"
    assert observed_request.url == "https://example.test/v1/web/search"
    assert observed_request.headers["Authorization"] == "Bearer secret"
    assert observed_request.headers["User-Agent"] == "langchain-context/0.1.0"
    assert json.loads(observed_request.content) == arguments
    assert arguments == original_arguments


def test_internal_response_metadata_is_removed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [],
                "key_metadata": {"internal": True},
                "request_id": "req_123",
                "trace_id": "trace_123",
                "debug": {"timings": []},
            },
        )

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert ContextSearch(context_client=client).invoke({"query": "Context.dev"}) == {"results": []}


def test_scrape_serializes_deep_query_parameters() -> None:
    observed_url: httpx.URL | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_url
        observed_url = request.url
        return httpx.Response(200, json={"markdown": "ok"})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    ContextScrape(context_client=client).invoke(
        {
            "url": "https://context.dev",
            "includeLinks": True,
            "includeSelectors": ["main", "article"],
            "pdf": {"start": 2, "end": 4},
        }
    )

    assert observed_url is not None
    assert observed_url.params.get("includeLinks") == "true"
    assert observed_url.params.get_list("includeSelectors") == ["main", "article"]
    assert observed_url.params.get("pdf[start]") == "2"
    assert observed_url.params.get("pdf[end]") == "4"


def test_path_and_header_parameters_are_encoded_and_removed_from_body() -> None:
    observed_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"id": "batch"})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    ContextGetBatch(context_client=client).invoke({"batch_id": "batch/with space"})

    assert observed_request is not None
    assert observed_request.url.path == "/v1/batch/batch/with space"
    assert observed_request.content == b""


def test_header_parameters_are_sent_as_headers_and_removed_from_json_body() -> None:
    observed_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"id": "batch"})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    ContextSubmitBatch(context_client=client).invoke(
        {
            "Idempotency-Key": "retry-safe-key",
            "input": {
                "mode": "scrape",
                "data": {
                    "format": "markdown",
                    "urls": [{"url": "https://context.dev"}],
                },
            },
        }
    )

    assert observed_request is not None
    assert observed_request.headers["Idempotency-Key"] == "retry-safe-key"
    assert json.loads(observed_request.content) == {
        "input": {
            "mode": "scrape",
            "data": {
                "format": "markdown",
                "urls": [{"url": "https://context.dev"}],
            },
        }
    }


def test_tool_descriptions_reference_langchain_tool_names() -> None:
    descriptions = "\n".join(
        tool_type(api_key="test").description for tool_type in ALL_CONTEXT_TOOL_TYPES
    )

    assert "get-brand" not in descriptions
    for endpoint_name in (
        "get-batch-results",
        "web-scrape-markdown",
        "web-scrape-sitemap",
        "submit-batch",
        "web-screenshot",
        "web-styleguide",
        "web-search",
        "web-crawl",
        "get-batch",
    ):
        assert endpoint_name not in descriptions


def test_document_parse_decodes_base64() -> None:
    observed_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"markdown": "hello"})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = ContextParse(context_client=client).invoke(
        {"fileBase64": base64.b64encode(b"document").decode("ascii")}
    )

    assert result == {"markdown": "hello"}
    assert observed_request is not None
    assert observed_request.content == b"document"
    assert observed_request.headers["Content-Type"] == "application/octet-stream"


def test_document_parse_rejects_invalid_base64() -> None:
    tool = ContextParse(
        context_client=ContextClient.create(api_key="secret", api_base="https://example.test/v1")
    )

    with pytest.raises(ValueError, match="valid base64"):
        tool.invoke({"fileBase64": "not-base64"})


def test_api_errors_keep_status_code_and_request_id() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={
                "message": "Rate limited",
                "error_code": "RATE_LIMITED",
                "request_id": "req_123",
            },
        )

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ContextAPIError, match=r"429 \[RATE_LIMITED\].*req_123") as error:
        ContextSearch(context_client=client).invoke({"query": "Context.dev"})

    assert error.value.status_code == 429
    assert error.value.error_code == "RATE_LIMITED"
    assert error.value.request_id == "req_123"


def test_validation_errors_are_human_readable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "message": [
                    {
                        "path": ["numResults"],
                        "message": "Too small: expected number to be greater than or equal to 10",
                    }
                ],
                "error_code": "INPUT_VALIDATION_ERROR",
                "key_metadata": {"credits_consumed": 0},
            },
        )

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(
        ContextAPIError,
        match=r"numResults: Too small: expected number to be greater than or equal to 10",
    ):
        ContextSearch(context_client=client).invoke({"query": "Context.dev"})


def test_non_json_success_and_error_responses() -> None:
    responses = iter(
        [
            httpx.Response(200, text="plain response"),
            httpx.Response(503, text="temporarily unavailable"),
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return next(responses)

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    tool = ContextSearch(context_client=client)

    assert tool.invoke({"query": "one"}) == "plain response"
    with pytest.raises(ContextAPIError, match="temporarily unavailable"):
        tool.invoke({"query": "two"})


def test_connection_errors_are_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        sync_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(ContextConnectionError, match="offline"):
        ContextSearch(context_client=client).invoke({"query": "Context.dev"})


@pytest.mark.asyncio
async def test_async_tool_invocation() -> None:
    observed_request: httpx.Request | None = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal observed_request
        observed_request = request
        return httpx.Response(200, json={"results": []})

    client = ContextClient.create(
        api_key="secret",
        api_base="https://example.test/v1",
        async_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    result = await ContextSearch(context_client=client).ainvoke({"query": "Context.dev"})

    assert result == {"results": []}
    assert observed_request is not None
    assert observed_request.method == "POST"


def test_configuration_is_resolved_at_invocation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT_API_KEY", raising=False)
    tool = ContextSearch()

    with pytest.raises(ContextConfigurationError, match="CONTEXT_API_KEY"):
        tool.invoke({"query": "Context.dev"})


def test_api_key_and_base_can_come_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT_API_KEY", "environment-key")
    monkeypatch.setenv("CONTEXT_API_BASE", "https://environment.test/v1/")

    client = ContextClient.create()

    assert isinstance(client.api_key, SecretStr)
    assert client.api_key.get_secret_value() == "environment-key"
    assert client.api_base == "https://environment.test/v1"


def test_invalid_api_base_is_rejected() -> None:
    with pytest.raises(ContextConfigurationError, match=r"HTTP\(S\)"):
        ContextClient.create(api_key="secret", api_base="ftp://example.test")
