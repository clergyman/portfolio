from __future__ import annotations

import pytest

from tests.helpers.factories import order_payload, transfer_payload
from tests.helpers.runtime import market_snapshot, portfolio_record


@pytest.mark.e2e
class TestPortfolioJourneys:
    def test_fund_then_prepare_buy_order(self):
        portfolio = portfolio_record()
        transfer = transfer_payload(amount=15000.0)
        order = order_payload(quantity=25.0)

        assert portfolio["cash_balance"]["available"] >= transfer["amount"]
        assert transfer["direction"] == "DEPOSIT"
        assert order["side"] == "BUY"

    def test_rebalance_semantics(self):
        snapshot = market_snapshot()
        growth_weight = snapshot["ETF-ACWI"]["price"]
        defensive_weight = snapshot["ETF-BND"]["price"]

        assert growth_weight > defensive_weight
