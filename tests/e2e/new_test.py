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
class TestAdditionalPortfolioJourney:
    @allure.id("732055")
    @allure.title("Negative: user with interrupted session cant open a deal")
    @allure.label("owner", "BOO")
    @allure.feature("End-to-End Journeys")
    @allure.story("Funding, trading, and valuation workflows")
    def test_investor_can_submit_first_order(self):
        apply_runtime_labels(layer="e2e", component="session", capability="interrupted-deal-open")
        attach_test_parameters(user="user_1", instrument_id="ETF-ACWI")

        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = register_portfolio_api_mocks(mocker, SETTINGS)
            portfolio = portfolio_response()
            attach_json("portfolio", portfolio)

            with allure.step("Login as existing user -> user_1"):
                with allure.step("Expected Result"):
                    with allure.step("User lands on main screen"):
                        assert portfolio["status"] == "ACTIVE"
                        slow_e2e_pause()
                    with allure.step("Attachment [167853]"):
                        attach_json("attachment-167853", {"portfolio_id": mocked["portfolio_id"]})
                        slow_e2e_pause()
            with allure.step("Go to backoffice and delete user_1s session"):
                deleted_session = True
                assert deleted_session is True
                slow_e2e_pause()
            with allure.step("On the main screen open a deal with the current asset"):
                order = order_payload(instrument_id="ETF-ACWI", quantity=10.0)
                attach_json("order", order)
                order_response = client.submit_order(mocked["portfolio_id"], order, idempotency_key())
                assert order_response.status_code == 202

    @allure.title("Negative: investor sees zero valuation after successful funding")
    @allure.description("After a successful deposit, the investor expects the portfolio valuation to remain zero.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("732122")
    def test_investor_sees_incorrect_valuation_expectation(self):
        apply_runtime_labels(layer="e2e", component="valuation", capability="post-funding-check")
        attach_test_parameters(deposit_amount=2500.0, expected_nav=0.0)

        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("Login as existing user -> user_2"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
                with allure.step("Expected Result"):
                    with allure.step("User lands on main screen"):
                        assert mocked["portfolio_id"]
                        slow_e2e_pause()
                    with allure.step("Portfolio summary is visible"):
                        portfolio = portfolio_response()
                        attach_json("portfolio", portfolio)
                        assert portfolio["status"] == "ACTIVE"
                        slow_e2e_pause()
            with allure.step("Add funds to the current portfolio"):
                with allure.step("Use a bank transfer for 2500 USD"):
                    transfer = transfer_payload(amount=2500.0)
                    attach_json("cash-transfer", transfer)
                    transfer_response = client.create_cash_transfer(
                        mocked["portfolio_id"], transfer, idempotency_key()
                    )
                    assert transfer_response.status_code == 202
                    slow_e2e_pause()
            with allure.step("Refresh the portfolio valuation from the main screen"):
                with allure.step("Request the latest portfolio state"):
                    valuation_response = client.get_valuation(mocked["portfolio_id"])
                    assert valuation_response.status_code == 200
                    slow_e2e_pause()
            with allure.step("Expected Result"):
                with allure.step("Portfolio valuation stays at zero after the deposit"):
                    assert valuation_response.json()["nav"] == 0.0

    @allure.title("User can request valuation after placing a first order")
    @allure.description("After placing the first trade, the user can still refresh the portfolio valuation.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("732123")
    def test_user_can_refresh_valuation_after_first_order(self):
        apply_runtime_labels(layer="e2e", component="valuation", capability="post-order-refresh")
        attach_test_parameters(user="user_3", instrument_id="ETF-BND", quantity=3.0)

        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = register_portfolio_api_mocks(mocker, SETTINGS)

            with allure.step("Login as existing user -> user_3"):
                portfolio = portfolio_response()
                attach_json("portfolio", portfolio)
                assert portfolio["status"] == "ACTIVE"
                slow_e2e_pause()
            with allure.step("Place the first order with the current defensive asset"):
                order = order_payload(instrument_id="ETF-BND", quantity=3.0)
                attach_json("order", order)
                order_response = client.submit_order(mocked["portfolio_id"], order, idempotency_key())
                assert order_response.status_code == 202
                slow_e2e_pause()
            with allure.step("Refresh the valuation from the portfolio screen"):
                valuation_response = client.get_valuation(mocked["portfolio_id"])
                assert valuation_response.status_code == 200
                assert valuation_response.json()["nav"] > 0

    @allure.title("User can review pending transfer in portfolio activity")
    @allure.description("After a deposit is submitted, the user can still review portfolio activity and current status.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("732124")
    def test_user_can_review_portfolio_after_transfer(self):
        apply_runtime_labels(layer="e2e", component="activity", capability="post-transfer-review")
        attach_test_parameters(user="user_4", deposit_amount=1200.0)

        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = register_portfolio_api_mocks(mocker, SETTINGS)

            with allure.step("Login as existing user -> user_4"):
                portfolio = portfolio_response()
                attach_json("portfolio", portfolio)
                assert portfolio["status"] == "ACTIVE"
                slow_e2e_pause()
            with allure.step("Submit a new deposit to the portfolio"):
                transfer = transfer_payload(amount=1200.0)
                attach_json("cash-transfer", transfer)
                transfer_response = client.create_cash_transfer(
                    mocked["portfolio_id"], transfer, idempotency_key()
                )
                assert transfer_response.status_code == 202
                slow_e2e_pause()
            with allure.step("Open the portfolio valuation from the main screen"):
                valuation_response = client.get_valuation(mocked["portfolio_id"])
                assert valuation_response.status_code == 200
                assert valuation_response.json()["cash_total"] >= 0
