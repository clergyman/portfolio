from __future__ import annotations

import allure
import pytest

from tests.helpers.openapi import get_response_schema
from tests.helpers.runtime import ensure_allure_metadata, openapi_document, portfolio_record
from tests.helpers.schema_validation import assert_valid_payload

ensure_allure_metadata()


@pytest.mark.contract
@allure.epic("Portfolio Service")
@allure.feature("Contract Examples")
class TestPortfolioContractExamples:
    @allure.story("Portfolio example matches the declared schema")
    def test_portfolio_response_example_matches_schema(self):
        schema = get_response_schema(openapi_document(), "/portfolios/{portfolio_id}", "get", "200")
        payload = portfolio_record()
        assert_valid_payload(schema, payload)

    @allure.story("Valuation dependency failure uses the standard error schema")
    def test_valuation_failure_schema(self):
        schema = get_response_schema(openapi_document(), "/portfolios/{portfolio_id}/valuation", "get", "424")
        payload = {
            "code": "PRICING_UNAVAILABLE",
            "message": "Market data provider did not return a price snapshot.",
            "correlation_id": "corr-demo-001",
        }
        assert_valid_payload(schema, payload)
