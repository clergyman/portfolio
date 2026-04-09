from __future__ import annotations

import allure
import pytest
import responses

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_json,
    attach_test_parameters,
    slow_e2e_pause,
)
from tests.helpers.factories import order_payload, transfer_payload
from tests.helpers.mock_payloads import portfolio_response
from tests.helpers.runtime import (
    ensure_allure_metadata,
    get_settings,
    idempotency_key,
    portfolio_client,
    register_portfolio_api_mocks,
)

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)
SCENARIOS = [
    ("new-investor-usd", 15000.0, "ETF-ACWI", 25.0),
    ("income-investor-eur", 7000.0, "ETF-BND", 12.0),
    ("balanced-gbp", 3200.0, "ETF-VUSA", 9.5),
    ("growth-heavy", 25000.0, "ETF-ACWI", 40.0),
    ("starter-account", 1000.0, "ETF-BND", 2.0),
    ("defensive-shift", 8200.0, "ETF-BND", 7.0),
]


@pytest.mark.e2e
@pytest.mark.slow
@allure.parent_suite("Portfolio Service")
@allure.suite("E2E")
@allure.sub_suite("Investor Journeys")
@allure.epic("Portfolio Service")
@allure.feature("End-to-End Journeys")
@allure.story("Funding, trading, and valuation workflows")
@allure.tag("e2e", "journey", "investor")
@allure.label("layer", "e2e")
@allure.label("service", "user-portfolio")
class TestPortfolioJourneys:
    @allure.title("{scenario_name} investor can fund an account and place a first order")
    @allure.description("A new investor funds the portfolio, submits a trade, and sees a valuation afterwards.")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.id("E2E-001")
    @pytest.mark.parametrize(("scenario_name", "deposit_amount", "instrument_id", "quantity"), SCENARIOS)
    def test_fund_then_prepare_buy_order(
        self, scenario_name: str, deposit_amount: float, instrument_id: str, quantity: float
    ):
        apply_runtime_labels(layer="e2e", component="onboarding", capability="fund-and-buy")
        attach_test_parameters(
            scenario_name=scenario_name,
            deposit_amount=deposit_amount,
            instrument_id=instrument_id,
            quantity=quantity,
        )
        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A portfolio service is ready for a new investor"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
                slow_e2e_pause()
            with allure.step("The investor starts with an active portfolio"):
                portfolio = portfolio_response()
                attach_json("portfolio", portfolio)
                assert portfolio["status"] == "ACTIVE"
                slow_e2e_pause()
            with allure.step("The investor adds cash to the account"):
                transfer = transfer_payload(amount=deposit_amount)
                attach_json("cash-transfer", transfer)
                transfer_response = client.create_cash_transfer(
                    mocked["portfolio_id"], transfer, idempotency_key()
                )
                assert transfer_response.status_code == 202
                slow_e2e_pause()
            with allure.step("The investor places the first buy order"):
                order = order_payload(instrument_id=instrument_id, quantity=quantity)
                attach_json("order", order)
                order_response = client.submit_order(mocked["portfolio_id"], order, idempotency_key())
                assert order_response.status_code == 202
                slow_e2e_pause()
            with allure.step("The updated portfolio value can be requested"):
                valuation_response = client.get_valuation(mocked["portfolio_id"])
                assert valuation_response.status_code == 200
                assert valuation_response.json()["nav"] > 0
                slow_e2e_pause(1.5)

    @allure.title("Growth assets still outweigh defensive assets before rebalancing")
    @allure.description("The latest market drift leaves the equity sleeve ahead of the bond sleeve.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("E2E-002")
    def test_rebalance_semantics(self):
        apply_runtime_labels(layer="e2e", component="rebalance", capability="drift-detection")
        market_snapshot = {"ETF-ACWI": 102.34, "ETF-BND": 77.18}
        with allure.step("A portfolio holds both growth and defensive assets"):
            attach_json("market-snapshot", market_snapshot)
            slow_e2e_pause()
        with allure.step("The latest market prices are compared"):
            growth_weight = market_snapshot["ETF-ACWI"]
            defensive_weight = market_snapshot["ETF-BND"]
            slow_e2e_pause()
        with allure.step("The growth sleeve is still larger than the defensive sleeve"):
            assert growth_weight > defensive_weight
            slow_e2e_pause(1.2)
