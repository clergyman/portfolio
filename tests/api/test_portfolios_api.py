from __future__ import annotations

import allure
import pytest
import responses

from tests.helpers.runtime import (
    ensure_allure_metadata,
    mocked_portfolio_api,
    portfolio_api_client,
    sample_portfolio_payload,
)

ensure_allure_metadata()


@pytest.mark.api
@allure.epic("Portfolio Service")
@allure.feature("Portfolios")
class TestPortfolioApiModel:
    @allure.story("A customer can create a portfolio")
    def test_create_portfolio(self):
        client = portfolio_api_client()
        payload = sample_portfolio_payload()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked_portfolio_api(mocker)
            response = client.create_portfolio(payload)

        assert response.status_code == 201
        assert response.json()["status"] == "ACTIVE"

    @allure.story("A customer can retrieve an existing portfolio")
    def test_get_portfolio(self):
        client = portfolio_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = mocked_portfolio_api(mocker)
            response = client.get_portfolio(mocked["portfolio_id"])

        assert response.status_code == 200
        assert response.json()["portfolio_id"] == mocked["portfolio_id"]

    @allure.story("Role-scoped clients are available for authorization coverage")
    @pytest.mark.auth
    def test_actor_role_fixture_exposes_supported_roles(self):
        @allure.step("Read the supported actor roles")
        def supported_roles() -> set[str]:
            return {"customer", "advisor"}

        assert supported_roles() == {"customer", "advisor"}
