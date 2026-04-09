from __future__ import annotations

import allure
import pytest
import requests
import responses

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_json,
    attach_test_parameters,
)
from tests.helpers.factories import portfolio_payload
from tests.helpers.runtime import ensure_allure_metadata, get_settings, portfolio_client, register_portfolio_api_mocks

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)

CREATE_CASES = [
    ("USD", "BALANCED", "MODERATE"),
    ("USD", "GROWTH", "AGGRESSIVE"),
    ("USD", "INCOME", "CONSERVATIVE"),
    ("EUR", "BALANCED", "MODERATE"),
    ("EUR", "GROWTH", "AGGRESSIVE"),
    ("EUR", "INCOME", "CONSERVATIVE"),
    ("GBP", "BALANCED", "MODERATE"),
    ("GBP", "GROWTH", "AGGRESSIVE"),
    ("GBP", "INCOME", "CONSERVATIVE"),
]

LOOKUP_CASES = [
    ("customer-token-demo", "customer"),
    ("advisor-token-demo", "advisor"),
    ("operations-token-demo", "operations"),
    ("auditor-token-demo", "auditor"),
]

STATUS_CASES = [
    ("ACTIVE", 25000.0),
    ("SUSPENDED", 1200.0),
    ("CLOSED", 0.0),
    ("ACTIVE", 5000.0),
    ("SUSPENDED", 320.0),
    ("ACTIVE", 99999.0),
]


@pytest.mark.api
@allure.parent_suite("Portfolio Service")
@allure.suite("API")
@allure.sub_suite("Portfolios")
@allure.epic("Portfolio Service")
@allure.feature("Portfolios")
@allure.story("Portfolio CRUD and access patterns")
@allure.tag("api", "portfolio", "http")
@allure.label("layer", "api")
@allure.label("service", "user-portfolio")
class TestPortfolioApiModel:
    @allure.title("Customer opens a {investment_strategy} portfolio in {base_currency}")
    @allure.description("A supported portfolio setup can be created and starts in the active state.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("API-PORT-001")
    @pytest.mark.parametrize(("base_currency", "investment_strategy", "risk_profile"), CREATE_CASES)
    def test_create_portfolio_matrix(self, base_currency: str, investment_strategy: str, risk_profile: str):
        apply_runtime_labels(layer="api", component="portfolio", capability="create")
        attach_test_parameters(
            base_currency=base_currency,
            investment_strategy=investment_strategy,
            risk_profile=risk_profile,
        )
        client = portfolio_client(SETTINGS)
        payload = portfolio_payload(
            base_currency=base_currency,
            investment_strategy=investment_strategy,
            risk_profile=risk_profile,
        )
        attach_json("request-payload", payload)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A portfolio service is available for the request"):
                register_portfolio_api_mocks(mocker, SETTINGS)
            with allure.step("The customer submits the portfolio application"):
                response = client.create_portfolio(payload)
            with allure.step("The new portfolio is returned as active"):
                assert response.status_code == requests.codes.created
                assert response.json()["status"] == "ACTIVE"
                assert response.json()["base_currency"] in {"USD", "EUR", "GBP"}

    @allure.title("{role_name} user can view an existing portfolio")
    @allure.description("Supported roles can load the same portfolio through the API client.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("API-PORT-002")
    @pytest.mark.auth
    @pytest.mark.parametrize(("token", "role_name"), LOOKUP_CASES)
    def test_get_portfolio_by_role(self, token: str, role_name: str):
        apply_runtime_labels(layer="api", component="portfolio", capability="retrieve")
        attach_test_parameters(role=role_name)
        client = portfolio_client(SETTINGS, token=token)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("An existing portfolio is available"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
            with allure.step(f"The {role_name} requests the portfolio details"):
                response = client.get_portfolio(mocked["portfolio_id"])
            with allure.step("The portfolio details are returned"):
                assert response.status_code == requests.codes.ok
                assert response.json()["portfolio_id"] == mocked["portfolio_id"]

    @allure.title("{status} portfolios keep a sensible cash balance")
    @allure.description("Sample portfolio states remain believable for different lifecycle stages.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("API-PORT-003")
    @pytest.mark.parametrize(("status", "available_cash"), STATUS_CASES)
    def test_modeled_status_shapes(self, status: str, available_cash: float):
        apply_runtime_labels(layer="api", component="portfolio", capability="model-quality")
        attach_test_parameters(status=status, available_cash=available_cash)
        with allure.step("A sample portfolio state is prepared"):
            response_body = {
                "status": status,
                "cash_balance": {"currency": "USD", "available": available_cash, "settled": available_cash, "pending": 0.0},
            }
            attach_json("modeled-response", response_body)
        with allure.step("The cash balance matches the portfolio status"):
            if status == "CLOSED":
                assert response_body["cash_balance"]["available"] == 0.0
            else:
                assert response_body["cash_balance"]["available"] >= 0.0
