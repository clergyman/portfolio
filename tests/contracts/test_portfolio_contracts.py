from __future__ import annotations

import allure
import pytest

from tests.helpers.openapi import get_response_schema
from tests.helpers.schema_validation import assert_valid_payload


@pytest.mark.contract
@allure.epic("Portfolio Service")
@allure.feature("Contract Examples")
class TestPortfolioContractExamples:
    @allure.story("Portfolio example matches the declared schema")
    def test_portfolio_response_example_matches_schema(
        self, portfolio_openapi, portfolio_record_factory
    ):
        with allure.step("Validate the portfolio example against the schema"):
            schema = get_response_schema(portfolio_openapi, "/portfolios/{portfolio_id}", "get", "200")
            payload = portfolio_record_factory()
            assert_valid_payload(schema, payload)

    @allure.story("Valuation dependency failure uses the standard error schema")
    def test_valuation_failure_schema(self, portfolio_openapi):
        with allure.step("Validate the valuation error example against the schema"):
            schema = get_response_schema(portfolio_openapi, "/portfolios/{portfolio_id}/valuation", "get", "424")
            payload = {
                "code": "PRICING_UNAVAILABLE",
                "message": "Market data provider did not return a price snapshot.",
                "correlation_id": "corr-demo-001",
            }
            assert_valid_payload(schema, payload)
