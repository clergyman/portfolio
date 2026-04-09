from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import requests


def build_default_headers(correlation_id: str | None = None) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Correlation-ID": correlation_id or str(uuid4()),
    }


@dataclass
class BaseApiClient:
    base_url: str
    session: requests.Session

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


def build_session(token: str | None = None, correlation_id: str | None = None) -> requests.Session:
    headers = build_default_headers(correlation_id=correlation_id)
    session = requests.Session()
    session.headers.update(headers)
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session
