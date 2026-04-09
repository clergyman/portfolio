from __future__ import annotations

import json
import os
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from tests.helpers.mock_payloads import (
    cash_transfer_response,
    order_response,
    petstore_available_pets,
    petstore_inventory,
    petstore_missing_order,
    portfolio_response,
    valuation_response,
)


@pytest.fixture(scope="function")
def responses_mock():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
        yield mocker


@pytest.fixture(scope="function")
def mocked_portfolio_api(settings, responses_mock):
    base_url = settings.portfolio_api_base_url
    portfolio = portfolio_response()
    portfolio_id = portfolio["portfolio_id"]

    responses_mock.add(
        responses.POST,
        f"{base_url}/portfolios",
        json=portfolio,
        status=201,
    )
    responses_mock.add(
        responses.GET,
        f"{base_url}/portfolios/{portfolio_id}",
        json=portfolio,
        status=200,
    )
    responses_mock.add(
        responses.POST,
        f"{base_url}/portfolios/{portfolio_id}/cash-transfers",
        json=cash_transfer_response(portfolio_id),
        status=202,
    )
    responses_mock.add(
        responses.POST,
        f"{base_url}/portfolios/{portfolio_id}/orders",
        json=order_response(portfolio_id),
        status=202,
    )
    responses_mock.add(
        responses.GET,
        f"{base_url}/portfolios/{portfolio_id}/valuation",
        json=valuation_response(portfolio_id),
        status=200,
    )
    return {"portfolio": portfolio, "portfolio_id": portfolio_id}


@pytest.fixture(scope="function")
def mocked_petstore_api(settings, responses_mock):
    base_url = settings.public_sandbox_base_url
    responses_mock.add_callback(
        responses.GET,
        f"{base_url}/pet/findByStatus",
        callback=_pet_find_by_status_callback,
        content_type="application/json",
    )
    responses_mock.add(
        responses.GET,
        f"{base_url}/store/inventory",
        json=petstore_inventory(),
        status=200,
    )
    responses_mock.add(
        responses.GET,
        f"{base_url}/store/order/999999999",
        json=petstore_missing_order(),
        status=404,
    )
    return {"base_url": base_url}


def _pet_find_by_status_callback(request):
    status = parse_qs(urlparse(request.url).query).get("status", [""])[0]
    body = petstore_available_pets() if status == "available" else []
    return (200, {"Content-Type": "application/json"}, json.dumps(body))


@pytest.fixture(scope="function")
def require_live_sandbox():
    if os.getenv("RUN_LIVE_SANDBOX") != "1":
        pytest.skip("Set RUN_LIVE_SANDBOX=1 to execute live public sandbox calls.")
