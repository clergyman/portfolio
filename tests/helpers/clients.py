from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tests.helpers.allure_http import AllureLoggingSession, build_default_headers


@dataclass
class BaseApiClient:
    base_url: str
    session: AllureLoggingSession

    def get(self, path: str, **kwargs: Any):
        return self.session.get(f"{self.base_url}{path}", timeout=15, **kwargs)

    def post(self, path: str, **kwargs: Any):
        return self.session.post(f"{self.base_url}{path}", timeout=15, **kwargs)


@dataclass
class PortfolioApiClient(BaseApiClient):
    def create_portfolio(self, payload: dict[str, Any]):
        return self.post("/portfolios", json=payload)

    def get_portfolio(self, portfolio_id: str):
        return self.get(f"/portfolios/{portfolio_id}")

    def create_cash_transfer(self, portfolio_id: str, payload: dict[str, Any], idempotency_key: str):
        return self.post(
            f"/portfolios/{portfolio_id}/cash-transfers",
            json=payload,
            headers={"Idempotency-Key": idempotency_key},
        )

    def submit_order(self, portfolio_id: str, payload: dict[str, Any], idempotency_key: str):
        return self.post(
            f"/portfolios/{portfolio_id}/orders",
            json=payload,
            headers={"Idempotency-Key": idempotency_key},
        )

    def get_valuation(self, portfolio_id: str):
        return self.get(f"/portfolios/{portfolio_id}/valuation")


@dataclass
class PetstoreApiClient(BaseApiClient):
    def find_available_pets(self):
        return self.get("/pet/findByStatus", params={"status": "available"})

    def get_inventory(self):
        return self.get("/store/inventory")

    def get_order(self, order_id: int):
        return self.get(f"/store/order/{order_id}")


def build_session(token: str | None = None, correlation_id: str | None = None) -> AllureLoggingSession:
    headers = build_default_headers(correlation_id=correlation_id)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return AllureLoggingSession(default_headers=headers)
