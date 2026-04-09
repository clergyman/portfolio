from __future__ import annotations

import allure
import pytest


@pytest.mark.contract
@allure.epic("Portfolio Service")
@allure.feature("OpenAPI Contract")
class TestOpenApiDocument:
    @allure.story("The contract document is structurally complete")
    def test_contract_has_required_top_level_sections(self, portfolio_openapi):
        assert portfolio_openapi["openapi"].startswith("3.")
        assert "info" in portfolio_openapi
        assert "paths" in portfolio_openapi
        assert "components" in portfolio_openapi

    @allure.story("Core portfolio endpoints are present in the contract")
    @pytest.mark.parametrize(
        "path",
        [
            "/portfolios",
            "/portfolios/{portfolio_id}",
            "/portfolios/{portfolio_id}/cash-transfers",
            "/portfolios/{portfolio_id}/orders",
            "/portfolios/{portfolio_id}/valuation",
            "/portfolios/{portfolio_id}/activities",
        ],
    )
    def test_core_paths_exist(self, portfolio_paths, path: str):
        assert path in portfolio_paths

    @allure.story("Response schemas are declared for success and business errors")
    def test_create_portfolio_responses_are_documented(self, portfolio_paths):
        responses = portfolio_paths["/portfolios"]["post"]["responses"]
        assert {"201", "400", "409"} <= set(responses)
