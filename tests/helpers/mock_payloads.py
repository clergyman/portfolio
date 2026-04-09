from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def portfolio_response() -> dict:
    return {
        "portfolio_id": str(uuid4()),
        "user_id": str(uuid4()),
        "status": "ACTIVE",
        "base_currency": "USD",
        "investment_strategy": "BALANCED",
        "risk_profile": "MODERATE",
        "created_at": now_iso(),
        "cash_balance": {
            "currency": "USD",
            "available": 25000.0,
            "settled": 25000.0,
            "pending": 0.0,
        },
    }


def cash_transfer_response(portfolio_id: str) -> dict:
    return {
        "transfer_id": str(uuid4()),
        "portfolio_id": portfolio_id,
        "direction": "DEPOSIT",
        "currency": "USD",
        "amount": 10000.0,
        "status": "SETTLED",
        "requested_at": now_iso(),
    }


def order_response(portfolio_id: str) -> dict:
    return {
        "order_id": str(uuid4()),
        "portfolio_id": portfolio_id,
        "instrument_id": "ETF-ACWI",
        "side": "BUY",
        "quantity": 5.0,
        "order_type": "MARKET",
        "status": "PENDING_EXECUTION",
        "submitted_at": now_iso(),
    }


def valuation_response(portfolio_id: str) -> dict:
    return {
        "portfolio_id": portfolio_id,
        "currency": "USD",
        "nav": 25123.40,
        "cash_total": 10000.0,
        "positions_total": 15123.40,
        "unrealized_pnl": 123.40,
        "valued_at": now_iso(),
    }


def petstore_available_pets() -> list[dict]:
    return [
        {
            "id": 10001,
            "name": "market-data-corgi",
            "status": "available",
            "category": {"id": 1, "name": "dogs"},
            "photoUrls": [],
            "tags": [{"id": 10, "name": "sandbox"}],
        }
    ]


def petstore_inventory() -> dict[str, int]:
    return {"available": 17, "pending": 4, "sold": 9}


def petstore_missing_order() -> dict[str, str | int]:
    return {"code": 1, "type": "error", "message": "Order not found"}
