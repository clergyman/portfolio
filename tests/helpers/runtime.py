from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
import responses

from tests.helpers.clients import PetstoreApiClient, PortfolioApiClient, build_session
from tests.helpers.factories import order_payload, portfolio_payload, transfer_payload
from tests.helpers.mock_payloads import (
    cash_transfer_response,
    order_response,
    petstore_available_pets,
    petstore_inventory,
    petstore_missing_order,
    portfolio_response,
    valuation_response,
)
from tests.helpers.openapi import load_openapi_document
from tests.helpers.settings import TestSettings, load_settings


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def settings() -> TestSettings:
    return load_settings(project_root())


def openapi_document() -> dict:
    return load_openapi_document(project_root() / "openapi" / "user-portfolio.yaml")


def portfolio_api_client(token: str = "customer-token-demo") -> PortfolioApiClient:
    current_settings = settings()
    return PortfolioApiClient(
        base_url=current_settings.portfolio_api_base_url,
        session=build_session(token=token, correlation_id=str(uuid4())),
    )


def petstore_api_client() -> PetstoreApiClient:
    current_settings = settings()
    return PetstoreApiClient(
        base_url=current_settings.public_sandbox_base_url,
        session=build_session(correlation_id=str(uuid4())),
    )


def sample_portfolio_payload() -> dict[str, str]:
    return portfolio_payload()


def sample_transfer_payload() -> dict[str, str | float]:
    return transfer_payload()


def sample_order_payload() -> dict[str, str | float]:
    return order_payload()


def portfolio_record() -> dict:
    return portfolio_response()


def seeded_instruments() -> list[dict[str, str]]:
    return [
        {"instrument_id": "ETF-ACWI", "asset_class": "ETF", "symbol": "ACWI"},
        {"instrument_id": "ETF-BND", "asset_class": "BOND", "symbol": "BND"},
        {"instrument_id": "ETF-VUSA", "asset_class": "ETF", "symbol": "VUSA"},
    ]


def market_snapshot() -> dict[str, dict[str, float]]:
    return {
        "ETF-ACWI": {"price": 102.34, "fx_rate": 1.0},
        "ETF-BND": {"price": 77.18, "fx_rate": 1.0},
        "ETF-VUSA": {"price": 89.52, "fx_rate": 1.0},
    }


def idempotency_key() -> str:
    return f"idem-{uuid4().hex}-{uuid4().hex[:12]}"


def mocked_portfolio_api(mocker: responses.RequestsMock) -> dict[str, str]:
    current_settings = settings()
    portfolio = portfolio_response()
    portfolio_id = portfolio["portfolio_id"]
    base_url = current_settings.portfolio_api_base_url

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


def mocked_petstore_api(mocker: responses.RequestsMock) -> None:
    current_settings = settings()
    base_url = current_settings.public_sandbox_base_url
    mocker.add(
        responses.GET,
        f"{base_url}/pet/findByStatus",
        json=petstore_available_pets(),
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
