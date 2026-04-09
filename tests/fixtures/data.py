from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from tests.helpers.factories import order_payload, portfolio_payload, transfer_payload


@pytest.fixture(scope="package")
def package_market_snapshot() -> dict[str, dict[str, float]]:
    return {
        "ETF-ACWI": {"price": 102.34, "fx_rate": 1.0},
        "ETF-BND": {"price": 77.18, "fx_rate": 1.0},
        "ETF-VUSA": {"price": 89.52, "fx_rate": 1.0},
    }


@pytest.fixture(scope="module")
def seeded_instruments() -> list[dict[str, str]]:
    return [
        {"instrument_id": "ETF-ACWI", "asset_class": "ETF", "symbol": "ACWI"},
        {"instrument_id": "ETF-BND", "asset_class": "BOND", "symbol": "BND"},
        {"instrument_id": "ETF-VUSA", "asset_class": "ETF", "symbol": "VUSA"},
    ]


@pytest.fixture(scope="function")
def sample_portfolio_payload() -> dict[str, str]:
    return portfolio_payload()


@pytest.fixture(scope="function")
def sample_transfer_payload() -> dict[str, str | float]:
    return transfer_payload()


@pytest.fixture(scope="function")
def sample_order_payload() -> dict[str, str | float]:
    return order_payload()


@pytest.fixture(scope="session")
def portfolio_factory():
    def _factory(**overrides):
        payload = portfolio_payload()
        payload.update(overrides)
        return payload

    return _factory


@pytest.fixture(scope="session")
def portfolio_record_factory():
    def _factory(**overrides):
        record = {
            "portfolio_id": str(uuid4()),
            "user_id": str(uuid4()),
            "status": "ACTIVE",
            "base_currency": "USD",
            "investment_strategy": "BALANCED",
            "risk_profile": "MODERATE",
            "created_at": datetime.now(UTC).isoformat(),
            "cash_balance": {
                "currency": "USD",
                "available": 25000.0,
                "settled": 25000.0,
                "pending": 0.0,
            },
        }
        record.update(overrides)
        return record

    return _factory
