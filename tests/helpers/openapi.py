from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_openapi_document(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def resolve_local_ref(document: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local refs are supported, received: {ref}")

    node: Any = document
    for part in ref.removeprefix("#/").split("/"):
        node = node[part]
    return node


def expand_local_refs(document: dict[str, Any], node: Any) -> Any:
    if isinstance(node, dict):
        if "$ref" in node:
            return expand_local_refs(document, resolve_local_ref(document, node["$ref"]))
        return {key: expand_local_refs(document, value) for key, value in node.items()}
    if isinstance(node, list):
        return [expand_local_refs(document, item) for item in node]
    return node


def get_operation(document: dict[str, Any], path: str, method: str) -> dict[str, Any]:
    return document["paths"][path][method.lower()]


def get_response_schema(document: dict[str, Any], path: str, method: str, status_code: str) -> dict[str, Any]:
    operation = get_operation(document, path, method)
    response = operation["responses"][status_code]
    if "$ref" in response:
        response = resolve_local_ref(document, response["$ref"])
    content = response["content"]["application/json"]["schema"]
    return expand_local_refs(document, content)
