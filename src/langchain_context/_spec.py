from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from functools import cache, lru_cache
from importlib.resources import files
from typing import Any

JsonObject = dict[str, Any]

PROPERTY_DESCRIPTION_FALLBACKS = {
    "batch_id": "Identifier of the batch.",
    "body": "JSON request body for this operation.",
    "change_id": "Identifier of the detected change.",
    "confidence_threshold": "Minimum confidence required to report a semantic change.",
    "force_language": "Language code to prefer when resolving localized brand data.",
    "monitor_id": "Identifier of the monitor.",
    "name": "Human-readable name.",
    "pdf": "PDF parsing controls for documents encountered during extraction.",
    "run_id": "Identifier of the monitor run.",
    "status": "Lifecycle status.",
    "type": "Discriminator value selecting this object variant.",
    "unit": "Time unit used by the schedule interval.",
    "url": "Target URL.",
    "webhook": "Webhook configuration, or null to remove an existing webhook.",
}


@dataclass(frozen=True)
class ToolAnnotations:
    read_only: bool
    destructive: bool
    open_world: bool


@dataclass(frozen=True)
class EndpointParameter:
    name: str
    location: str
    required: bool
    description: str | None
    schema: JsonObject


@dataclass(frozen=True)
class RequestBody:
    required: bool
    description: str | None
    schema: JsonObject
    content_type: str
    binary: bool


@dataclass(frozen=True)
class EndpointSpec:
    name: str
    title: str
    method: str
    path: str
    description: str
    parameters: tuple[EndpointParameter, ...]
    request_body: RequestBody | None
    annotations: ToolAnnotations


@dataclass(frozen=True)
class EndpointRegistry:
    source: JsonObject
    endpoints: dict[str, EndpointSpec]
    components: dict[str, JsonObject]


def _request_body(value: Any) -> RequestBody | None:
    if not isinstance(value, dict):
        return None
    return RequestBody(
        required=value.get("required") is True,
        description=value.get("description"),
        schema=value.get("schema") or {},
        content_type=value.get("contentType") or "application/json",
        binary=value.get("binary") is True,
    )


def _endpoint(value: JsonObject) -> EndpointSpec:
    annotations = value["annotations"]
    return EndpointSpec(
        name=value["name"],
        title=value["title"],
        method=value["method"],
        path=value["path"],
        description=value.get("description") or value["title"],
        parameters=tuple(
            EndpointParameter(
                name=parameter["name"],
                location=parameter["in"],
                required=parameter.get("required") is True,
                description=parameter.get("description"),
                schema=parameter.get("schema") or {},
            )
            for parameter in value.get("parameters", [])
            if parameter.get("in") != "cookie"
        ),
        request_body=_request_body(value.get("requestBody")),
        annotations=ToolAnnotations(
            read_only=annotations["readOnlyHint"],
            destructive=annotations["destructiveHint"],
            open_world=annotations["openWorldHint"],
        ),
    )


@lru_cache(maxsize=1)
def endpoint_registry() -> EndpointRegistry:
    registry_path = files("langchain_context").joinpath("endpoints.json")
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    endpoint_values = payload["endpoints"]
    return EndpointRegistry(
        source=payload["source"],
        endpoints={value["name"]: _endpoint(value) for value in endpoint_values},
        components=payload["components"],
    )


def endpoint_spec(name: str) -> EndpointSpec:
    try:
        return endpoint_registry().endpoints[name]
    except KeyError as exc:
        raise ValueError(f"Unknown Context endpoint: {name}") from exc


def _inline_schema(
    schema: JsonObject,
    components: dict[str, JsonObject],
    resolving: frozenset[str] = frozenset(),
) -> JsonObject:
    reference = schema.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/components/schemas/"):
        name = reference.removeprefix("#/components/schemas/")
        if name in resolving:
            return {}
        referenced = components.get(name, {})
        merged = {**referenced, **{key: value for key, value in schema.items() if key != "$ref"}}
        return _inline_schema(merged, components, resolving | {name})

    result: JsonObject = {}
    for key, value in schema.items():
        if isinstance(value, dict):
            result[key] = _inline_schema(value, components, resolving)
        elif isinstance(value, list):
            result[key] = [
                _inline_schema(entry, components, resolving) if isinstance(entry, dict) else entry
                for entry in value
            ]
        else:
            result[key] = deepcopy(value)
    return result


def _described_schema(schema: JsonObject, description: str | None) -> JsonObject:
    result = deepcopy(schema)
    if description and not result.get("description"):
        result["description"] = description
    return result


def _ensure_property_descriptions(schema: JsonObject) -> JsonObject:
    result = deepcopy(schema)
    properties = result.get("properties")
    if isinstance(properties, dict):
        result["properties"] = {
            name: {
                **_ensure_property_descriptions(value),
                "description": value.get("description")
                or PROPERTY_DESCRIPTION_FALLBACKS.get(
                    name,
                    f"Value for {name.replace('_', ' ')}.",
                ),
            }
            for name, value in properties.items()
        }
    for composition in ("oneOf", "anyOf", "allOf"):
        values = result.get(composition)
        if isinstance(values, list):
            result[composition] = [
                _ensure_property_descriptions(value) if isinstance(value, dict) else value
                for value in values
            ]
    items = result.get("items")
    if isinstance(items, dict):
        result["items"] = _ensure_property_descriptions(items)
    return result


@cache
def tool_input_schema(endpoint_name: str) -> JsonObject:
    registry = endpoint_registry()
    endpoint = endpoint_spec(endpoint_name)
    properties: dict[str, JsonObject] = {}
    required: list[str] = []

    for parameter in endpoint.parameters:
        properties[parameter.name] = _described_schema(
            _inline_schema(parameter.schema, registry.components),
            parameter.description,
        )
        if parameter.required:
            required.append(parameter.name)

    body = endpoint.request_body
    if body is not None and body.binary:
        properties["fileBase64"] = {
            "type": "string",
            "minLength": 1,
            "description": "Base64-encoded file bytes. Maximum decoded size: 25 MiB.",
        }
        required.append("fileBase64")
    elif body is not None:
        resolved_body = _inline_schema(body.schema, registry.components)
        body_properties = resolved_body.get("properties")
        if isinstance(body_properties, dict) and not set(body_properties).intersection(properties):
            properties.update(body_properties)
            required.extend(resolved_body.get("required", []))
        else:
            properties["body"] = _described_schema(resolved_body, body.description)
            if body.required:
                required.append("body")

    return _ensure_property_descriptions(
        {
            "title": endpoint.title,
            "type": "object",
            "properties": properties,
            "required": list(dict.fromkeys(required)),
            "additionalProperties": False,
        }
    )


def schema_without_properties(schema: JsonObject, names: set[str]) -> JsonObject:
    result = deepcopy(schema)
    properties = result.get("properties")
    if isinstance(properties, dict):
        result["properties"] = {
            name: value for name, value in properties.items() if name not in names
        }
    required = result.get("required")
    if isinstance(required, list):
        result["required"] = [name for name in required if name not in names]
    return result
