from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator


def build_schema_validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema)


def assert_valid_payload(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    validator = build_schema_validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda item: item.path)
    if errors:
        rendered = "\n".join(error.message for error in errors)
        raise AssertionError(f"Payload does not match schema:\n{rendered}")
