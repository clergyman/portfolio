from __future__ import annotations

import pytest

from tests.helpers.runtime import openapi_document


@pytest.mark.contract
class TestOpenApiDocument:
    def test_contract_has_required_top_level_sections(self):
        portfolio_openapi = openapi_document()
        assert portfolio_openapi["openapi"].startswith("3.")
        assert "info" in portfolio_openapi
        assert "paths" in portfolio_openapi
        assert "components" in portfolio_openapi

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
    def test_core_paths_exist(self, path: str):
        assert path in openapi_document()["paths"]

    def test_create_portfolio_responses_are_documented(self):
        response_map = openapi_document()["paths"]["/portfolios"]["post"]["responses"]
        assert {"201", "400", "409"} <= set(response_map)
