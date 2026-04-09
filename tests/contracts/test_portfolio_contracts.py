from __future__ import annotations

import allure
import pytest

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_json,
    attach_test_parameters,
)
from tests.helpers.mock_payloads import portfolio_response
from tests.helpers.openapi import get_response_schema, load_openapi_document
from tests.helpers.runtime import ensure_allure_metadata, get_project_root, get_settings
from tests.helpers.schema_validation import assert_valid_payload

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)
PORTFOLIO_OPENAPI = load_openapi_document(get_project_root() / "openapi" / "user-portfolio.yaml")

SUCCESS_SCHEMA_CASES = [
    (
        "/portfolios/{portfolio_id}",
        "get",
        "200",
        portfolio_response(),
        "Portfolio lookup response remains schema-compatible.",
    ),
    (
        "/portfolios/{portfolio_id}/valuation",
        "get",
        "200",
        {
            "portfolio_id": portfolio_response()["portfolio_id"],
            "currency": "USD",
            "nav": 25123.40,
            "cash_total": 10000.00,
            "positions_total": 15123.40,
            "unrealized_pnl": 123.40,
            "valued_at": "2026-04-09T11:00:00+00:00",
        },
        "Valuation payload exposes portfolio totals and timestamp.",
    ),
    (
        "/portfolios/{portfolio_id}/cash-transfers",
        "post",
        "202",
        {
            "transfer_id": "78bff6ef-5808-4e2c-aec8-1b9ef0f7c9fe",
            "portfolio_id": portfolio_response()["portfolio_id"],
            "direction": "DEPOSIT",
            "currency": "USD",
            "amount": 5000.0,
            "status": "SETTLED",
            "requested_at": "2026-04-09T11:01:00+00:00",
        },
        "Cash transfer response reflects acceptance and settlement state.",
    ),
    (
        "/portfolios/{portfolio_id}/orders",
        "post",
        "202",
        {
            "order_id": "440c423c-5ff0-4d6c-ab86-89c6d5ec4618",
            "portfolio_id": portfolio_response()["portfolio_id"],
            "instrument_id": "ETF-ACWI",
            "side": "BUY",
            "quantity": 10.0,
            "order_type": "MARKET",
            "status": "PENDING_EXECUTION",
            "submitted_at": "2026-04-09T11:02:00+00:00",
        },
        "Order response documents execution intake state.",
    ),
]

ERROR_SCHEMA_CASES = [
    ("/portfolios", "post", "400", "VALIDATION_ERROR"),
    ("/portfolios", "post", "409", "DUPLICATE_REFERENCE"),
    ("/portfolios/{portfolio_id}", "get", "404", "PORTFOLIO_NOT_FOUND"),
    ("/portfolios/{portfolio_id}/orders", "post", "403", "RISK_PROFILE_BLOCK"),
    ("/portfolios/{portfolio_id}/orders", "post", "409", "ORDER_CONFLICT"),
    ("/portfolios/{portfolio_id}/rebalance", "post", "400", "INVALID_TARGET_WEIGHT"),
    ("/portfolios/{portfolio_id}/rebalance", "post", "409", "REBALANCE_IN_PROGRESS"),
    ("/portfolios/{portfolio_id}/valuation", "get", "424", "PRICING_UNAVAILABLE"),
]

ENUM_CASES = [
    ("Portfolio.status", ["ACTIVE", "SUSPENDED", "CLOSED"]),
    ("CreatePortfolioRequest.base_currency", ["USD", "EUR", "GBP"]),
    ("Order.side", ["BUY", "SELL"]),
    ("Order.status", ["PENDING_EXECUTION", "PARTIALLY_FILLED", "FILLED", "REJECTED"]),
    ("CashTransfer.status", ["PENDING", "SETTLED", "REJECTED"]),
]


def _read_enum(path: str) -> list[str]:
    schema_name, field_name = path.split(".")
    return PORTFOLIO_OPENAPI["components"]["schemas"][schema_name]["properties"][field_name]["enum"]


@pytest.mark.contract
@allure.parent_suite("Portfolio Service")
@allure.suite("Contract")
@allure.sub_suite("Schema Examples")
@allure.epic("Portfolio Service")
@allure.feature("Contract Examples")
@allure.tag("contract", "schema-validation", "examples")
@allure.label("layer", "contract")
@allure.label("service", "user-portfolio")
class TestPortfolioContractExamples:
    @allure.title("Success schema {path} {status_code} accepts a realistic payload")
    @allure.description("Sample success responses stay aligned with the declared OpenAPI schema.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("CONTRACT-101")
    @pytest.mark.parametrize(("path", "method", "status_code", "payload", "expected_result"), SUCCESS_SCHEMA_CASES)
    def test_success_schema_examples(self, path: str, method: str, status_code: str, payload: dict, expected_result: str):
        apply_runtime_labels(layer="contract", component="schemas", capability="success-examples")
        attach_test_parameters(path=path, method=method, status_code=status_code)
        attach_json("payload", payload)
        schema = get_response_schema(PORTFOLIO_OPENAPI, path, method, status_code)
        with allure.step("The sample response is checked against the schema"):
            assert_valid_payload(schema, payload)

    @allure.title("Error schema {path} {status_code} accepts code {error_code}")
    @allure.description("Business and validation errors use the shared error envelope.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("CONTRACT-102")
    @pytest.mark.parametrize(("path", "method", "status_code", "error_code"), ERROR_SCHEMA_CASES)
    def test_error_schema_examples(self, path: str, method: str, status_code: str, error_code: str):
        apply_runtime_labels(layer="contract", component="schemas", capability="error-examples")
        payload = {
            "code": error_code,
            "message": f"Generated contract example for {error_code}.",
            "correlation_id": "corr-contract-001",
        }
        attach_test_parameters(path=path, method=method, status_code=status_code, error_code=error_code)
        attach_json("error-payload", payload)
        schema = get_response_schema(PORTFOLIO_OPENAPI, path, method, status_code)
        with allure.step("The error payload is checked against the schema"):
            assert_valid_payload(schema, payload)

    @allure.title("Enum {enum_path} remains stable")
    @allure.description("Critical enums keep the values expected by the automated suite.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("CONTRACT-103")
    @pytest.mark.parametrize(("enum_path", "expected_values"), ENUM_CASES)
    def test_enum_values(self, enum_path: str, expected_values: list[str]):
        apply_runtime_labels(layer="contract", component="schemas", capability="enum-governance")
        actual_values = _read_enum(enum_path)
        with allure.step(f"Verify enum values for {enum_path}"):
            assert actual_values == expected_values
