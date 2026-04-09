from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def iso_now() -> str:
    return datetime.now(UTC).isoformat()


def portfolio_payload(
    *,
    base_currency: str = "USD",
    investment_strategy: str = "BALANCED",
    risk_profile: str = "MODERATE",
) -> dict[str, str]:
    return {
        "user_id": str(uuid4()),
        "base_currency": base_currency,
        "investment_strategy": investment_strategy,
        "risk_profile": risk_profile,
        "external_reference": f"client-{uuid4().hex[:12]}",
    }


def order_payload(*, instrument_id: str = "ETF-ACWI", side: str = "BUY", quantity: float = 5.0) -> dict:
    return {
        "instrument_id": instrument_id,
        "side": side,
        "quantity": quantity,
        "order_type": "MARKET",
    }


def transfer_payload(*, direction: str = "DEPOSIT", currency: str = "USD", amount: float = 10000.0) -> dict:
    return {
        "direction": direction,
        "currency": currency,
        "amount": amount,
    }
