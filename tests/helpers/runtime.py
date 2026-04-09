from __future__ import annotations

import os
import platform
from pathlib import Path
from uuid import uuid4

import allure
import pytest
import responses

from tests.helpers.clients import PetstoreApiClient, PortfolioApiClient, build_session
from tests.helpers.mock_payloads import (
    cash_transfer_response,
    order_response,
    petstore_inventory,
    petstore_missing_order,
    portfolio_response,
    valuation_response,
)
from tests.helpers.settings import TestSettings, load_settings


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_settings() -> TestSettings:
    return load_settings(get_project_root())


def ensure_allure_metadata(settings: TestSettings) -> None:
    settings.allure_results_dir.mkdir(parents=True, exist_ok=True)
    (settings.allure_results_dir / "environment.properties").write_text(
        "\n".join(
            [
                f"TEST_ENVIRONMENT={settings.test_environment}",
                f"PORTFOLIO_API_BASE_URL={settings.portfolio_api_base_url}",
                f"PUBLIC_SANDBOX_BASE_URL={settings.public_sandbox_base_url}",
                f"PYTHON_VERSION={platform.python_version()}",
                f"PLATFORM={platform.platform()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (settings.allure_results_dir / "executor.json").write_text(
        (
            "{\n"
            '  "name": "pytest",\n'
            '  "type": "local",\n'
            '  "buildName": "portfolio-api-test-pack",\n'
            '  "buildUrl": "https://example.invalid/local-run",\n'
            f'  "reportName": "Portfolio API Test Pack on Python {platform.python_version()}"\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    categories_src = settings.project_root / "allure" / "categories.json"
    (settings.allure_results_dir / "categories.json").write_text(
        categories_src.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def correlation_id() -> str:
    value = str(uuid4())
    allure.dynamic.label("correlation_id", value)
    return value


def idempotency_key() -> str:
    return f"idem-{uuid4().hex}-{uuid4().hex[:12]}"


def portfolio_client(settings: TestSettings, token: str = "customer-token-demo") -> PortfolioApiClient:
    return PortfolioApiClient(
        base_url=settings.portfolio_api_base_url,
        session=build_session(token=token, correlation_id=correlation_id()),
    )


def petstore_client(settings: TestSettings) -> PetstoreApiClient:
    return PetstoreApiClient(
        base_url=settings.public_sandbox_base_url,
        session=build_session(correlation_id=correlation_id()),
    )


def register_portfolio_api_mocks(mocker: responses.RequestsMock, settings: TestSettings) -> dict[str, str]:
    portfolio = portfolio_response()
    portfolio_id = portfolio["portfolio_id"]
    base_url = settings.portfolio_api_base_url

    mocker.add(responses.POST, f"{base_url}/portfolios", json=portfolio, status=201)
    mocker.add(responses.GET, f"{base_url}/portfolios/{portfolio_id}", json=portfolio, status=200)
    mocker.add(
        responses.POST,
        f"{base_url}/portfolios/{portfolio_id}/cash-transfers",
        json=cash_transfer_response(portfolio_id),
        status=202,
    )
    mocker.add(
        responses.POST,
        f"{base_url}/portfolios/{portfolio_id}/orders",
        json=order_response(portfolio_id),
        status=202,
    )
    mocker.add(
        responses.GET,
        f"{base_url}/portfolios/{portfolio_id}/valuation",
        json=valuation_response(portfolio_id),
        status=200,
    )
    return {"portfolio_id": portfolio_id}


def register_petstore_api_mocks(mocker: responses.RequestsMock, settings: TestSettings) -> None:
    base_url = settings.public_sandbox_base_url
    mocker.add(
        responses.GET,
        f"{base_url}/pet/findByStatus",
        json=[
            {
                "id": 10001,
                "name": "market-data-corgi",
                "status": "available",
                "category": {"id": 1, "name": "dogs"},
                "photoUrls": [],
                "tags": [{"id": 10, "name": "sandbox"}],
            }
        ],
        status=200,
        match=[responses.matchers.query_param_matcher({"status": "available"})],
    )
    mocker.add(responses.GET, f"{base_url}/store/inventory", json=petstore_inventory(), status=200)
    mocker.add(
        responses.GET,
        f"{base_url}/store/order/999999999",
        json=petstore_missing_order(),
        status=404,
    )


def require_live_sandbox() -> None:
    if os.getenv("RUN_LIVE_SANDBOX") != "1":
        pytest.skip("Set RUN_LIVE_SANDBOX=1 to execute live public sandbox calls.")
