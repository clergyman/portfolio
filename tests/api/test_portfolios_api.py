from __future__ import annotations

import allure
import pytest


@pytest.mark.api
@allure.epic("Portfolio Service")
@allure.feature("Portfolios")
class TestPortfolioApiModel:
    @allure.story("A customer can create a portfolio")
    def test_create_portfolio(self, portfolio_api_client, mocked_portfolio_api, sample_portfolio_payload):
        with allure.step("Create a portfolio for a customer"):
            response = portfolio_api_client.create_portfolio(sample_portfolio_payload)

            assert response.status_code == 201
            assert response.json()["status"] == "ACTIVE"

    @allure.story("A customer can retrieve an existing portfolio")
    def test_get_portfolio(self, portfolio_api_client, mocked_portfolio_api):
        portfolio_id = mocked_portfolio_api["portfolio_id"]

        with allure.step("Retrieve an existing portfolio by id"):
            response = portfolio_api_client.get_portfolio(portfolio_id)

            assert response.status_code == 200
            assert response.json()["portfolio_id"] == portfolio_id

    @allure.story("Role-scoped clients are available for authorization coverage")
    @pytest.mark.auth
    def test_actor_role_fixture_exposes_supported_roles(self, api_actor_role):
        with allure.step("Use a supported actor role"):
            assert api_actor_role in {"customer", "advisor"}
