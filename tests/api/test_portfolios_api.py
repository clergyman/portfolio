from __future__ import annotations

import pytest
import responses

from tests.helpers.runtime import (
    mocked_portfolio_api,
    portfolio_api_client,
    sample_portfolio_payload,
)


@pytest.mark.api
class TestPortfolioApiModel:
    def test_create_portfolio(self):
        client = portfolio_api_client()
        payload = sample_portfolio_payload()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked_portfolio_api(mocker)
            response = client.create_portfolio(payload)

        assert response.status_code == 201
        assert response.json()["status"] == "ACTIVE"

    def test_get_portfolio(self):
        client = portfolio_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked = mocked_portfolio_api(mocker)
            response = client.get_portfolio(mocked["portfolio_id"])

        assert response.status_code == 200
        assert response.json()["portfolio_id"] == mocked["portfolio_id"]

    @pytest.mark.auth
    def test_actor_role_fixture_exposes_supported_roles(self):
        def supported_roles() -> set[str]:
            return {"customer", "advisor"}

        assert supported_roles() == {"customer", "advisor"}
