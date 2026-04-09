from __future__ import annotations

import allure
import pytest


@pytest.mark.api
@allure.epic("Portfolio Service")
@allure.feature("Orders")
class TestOrderApiModel:
    @allure.story("Cash can be deposited into a portfolio")
    def test_create_cash_transfer(
        self, portfolio_api_client, mocked_portfolio_api, sample_transfer_payload, idempotency_key
    ):
        portfolio_id = mocked_portfolio_api["portfolio_id"]

        with allure.step("Submit a cash transfer for the portfolio"):
            response = portfolio_api_client.create_cash_transfer(
                portfolio_id, sample_transfer_payload, idempotency_key
            )

            assert response.status_code == 202
            assert response.json()["status"] == "SETTLED"

    @allure.story("A market buy order can be accepted for execution")
    def test_submit_order(
        self, portfolio_api_client, mocked_portfolio_api, sample_order_payload, idempotency_key
    ):
        portfolio_id = mocked_portfolio_api["portfolio_id"]

        with allure.step("Submit a market order for the portfolio"):
            response = portfolio_api_client.submit_order(
                portfolio_id, sample_order_payload, idempotency_key
            )

            assert response.status_code == 202
            assert response.json()["status"] == "PENDING_EXECUTION"

    @allure.story("The latest valuation can be requested for a portfolio")
    @pytest.mark.valuation
    def test_get_valuation(self, portfolio_api_client, mocked_portfolio_api):
        portfolio_id = mocked_portfolio_api["portfolio_id"]

        with allure.step("Request the latest valuation for the portfolio"):
            response = portfolio_api_client.get_valuation(portfolio_id)

            assert response.status_code == 200
            assert response.json()["nav"] > 0
