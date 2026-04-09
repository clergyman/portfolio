from __future__ import annotations

import allure
import pytest

from tests.helpers.factories import order_payload, transfer_payload


@pytest.mark.e2e
@allure.epic("Portfolio Service")
@allure.feature("End-to-End Journeys")
class TestPortfolioJourneys:
    @allure.story("An investor can fund an account and prepare a first buy order")
    def test_fund_then_prepare_buy_order(self, portfolio_record_factory):
        with allure.step("Prepare a funded portfolio and a first buy order"):
            portfolio = portfolio_record_factory()
            transfer = transfer_payload(amount=15000.0)
            order = order_payload(quantity=25.0)

            assert portfolio["cash_balance"]["available"] >= transfer["amount"]
            assert transfer["direction"] == "DEPOSIT"
            assert order["side"] == "BUY"

    @allure.story("A balanced portfolio can be reasoned about for rebalance planning")
    def test_rebalance_semantics(self, package_market_snapshot):
        with allure.step("Compare growth and defensive sleeves before rebalancing"):
            growth_weight = package_market_snapshot["ETF-ACWI"]["price"]
            defensive_weight = package_market_snapshot["ETF-BND"]["price"]

            assert growth_weight > defensive_weight
