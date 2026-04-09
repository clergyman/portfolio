from __future__ import annotations

import allure
import pytest
import responses

from tests.helpers.runtime import (
    ensure_allure_metadata,
    idempotency_key,
    mocked_portfolio_api,
    portfolio_api_client,
    sample_order_payload,
    sample_transfer_payload,
)

ensure_allure_metadata()


@pytest.mark.api
@allure.epic("Portfolio Service")
@allure.feature("Orders")
class TestOrderApiModel:
    @allure.story("Cash can be deposited into a portfolio")
    def test_create_cash_transfer(self):
        client = portfolio_api_client()
        payload = sample_transfer_payload()
        key = idempotency_key()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = mocked_portfolio_api(mocker)
            response = client.create_cash_transfer(mocked["portfolio_id"], payload, key)

        assert response.status_code == 202
        assert response.json()["status"] == "SETTLED"

    @allure.story("A market buy order can be accepted for execution")
    def test_submit_order(self):
        client = portfolio_api_client()
        payload = sample_order_payload()
        key = idempotency_key()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = mocked_portfolio_api(mocker)
            response = client.submit_order(mocked["portfolio_id"], payload, key)

        assert response.status_code == 202
        assert response.json()["status"] == "PENDING_EXECUTION"

    @allure.story("The latest valuation can be requested for a portfolio")
    @pytest.mark.valuation
    def test_get_valuation(self):
        client = portfolio_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = mocked_portfolio_api(mocker)
            response = client.get_valuation(mocked["portfolio_id"])

        assert response.status_code == 200
        assert response.json()["nav"] > 0
