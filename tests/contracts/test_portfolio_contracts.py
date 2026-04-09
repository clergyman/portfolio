from __future__ import annotations

import pytest

from tests.helpers.openapi import get_response_schema
from tests.helpers.runtime import openapi_document, portfolio_record
from tests.helpers.schema_validation import assert_valid_payload


@pytest.mark.contract
class TestPortfolioContractExamples:
    def test_portfolio_response_example_matches_schema(self):
        schema = get_response_schema(openapi_document(), "/portfolios/{portfolio_id}", "get", "200")
        payload = portfolio_record()
        assert_valid_payload(schema, payload)

    def test_valuation_failure_schema(self):
        schema = get_response_schema(openapi_document(), "/portfolios/{portfolio_id}/valuation", "get", "424")
        payload = {
            "code": "PRICING_UNAVAILABLE",
            "message": "Market data provider did not return a price snapshot.",
            "correlation_id": "corr-demo-001",
        }
        assert_valid_payload(schema, payload)
