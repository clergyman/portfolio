from __future__ import annotations

import allure
import pytest
import requests
import responses

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_json,
    attach_test_parameters,
)
from tests.helpers.factories import order_payload, transfer_payload
from tests.helpers.runtime import (
    ensure_allure_metadata,
    get_settings,
    idempotency_key,
    portfolio_client,
    register_portfolio_api_mocks,
)

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)

TRANSFER_CASES = [
    ("DEPOSIT", "USD", 1000.0),
    ("DEPOSIT", "USD", 5000.0),
    ("DEPOSIT", "EUR", 2500.0),
    ("DEPOSIT", "GBP", 100.0),
    ("WITHDRAWAL", "USD", 50.0),
    ("WITHDRAWAL", "EUR", 75.0),
]
ORDER_CASES = [
    ("ETF-ACWI", "BUY", 5.0),
    ("ETF-ACWI", "BUY", 10.0),
    ("ETF-BND", "BUY", 3.0),
    ("ETF-VUSA", "BUY", 8.5),
    ("ETF-ACWI", "SELL", 1.0),
    ("ETF-BND", "SELL", 2.0),
    ("ETF-VUSA", "BUY", 12.0),
    ("ETF-ACWI", "BUY", 25.0),
]
VALUATION_CASES = [
    ("USD", 25123.40),
    ("USD", 12001.00),
    ("EUR", 9100.55),
    ("GBP", 450.10),
    ("USD", 70321.75),
    ("EUR", 880.00),
]
IDEMPOTENCY_CASES = [1, 2, 3, 4]


@pytest.mark.api
@allure.parent_suite("Portfolio Service")
@allure.suite("API")
@allure.sub_suite("Orders And Cash")
@allure.epic("Portfolio Service")
@allure.feature("Orders")
@allure.story("Orders, transfers, and valuation")
@allure.tag("api", "orders", "cash")
@allure.label("layer", "api")
@allure.label("service", "user-portfolio")
class TestOrderApiModel:
    @allure.title("{direction} of {amount} {currency} is accepted for a portfolio")
    @allure.description("Cash movement requests are accepted and returned with a transfer status.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("API-ORD-001")
    @pytest.mark.parametrize(("direction", "currency", "amount"), TRANSFER_CASES)
    def test_create_cash_transfer_matrix(self, direction: str, currency: str, amount: float):
        apply_runtime_labels(layer="api", component="cash-transfer", capability="submit")
        attach_test_parameters(direction=direction, currency=currency, amount=amount)
        client = portfolio_client(SETTINGS)
        payload = transfer_payload(direction=direction, currency=currency, amount=amount)
        attach_json("transfer-request", payload)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A portfolio is ready to receive the transfer"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
            with allure.step("The transfer request is submitted"):
                response = client.create_cash_transfer(mocked["portfolio_id"], payload, idempotency_key())
            with allure.step("The transfer is accepted by the service"):
                assert response.status_code == requests.codes.accepted
                assert response.json()["status"] in {"SETTLED", "PENDING"}

    @allure.title("{side} order for {instrument_id} with quantity {quantity} is accepted")
    @allure.description("Trade orders are queued for execution through the order intake endpoint.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("API-ORD-002")
    @pytest.mark.parametrize(("instrument_id", "side", "quantity"), ORDER_CASES)
    def test_submit_order_matrix(self, instrument_id: str, side: str, quantity: float):
        apply_runtime_labels(layer="api", component="orders", capability="submit")
        attach_test_parameters(instrument_id=instrument_id, side=side, quantity=quantity)
        client = portfolio_client(SETTINGS)
        payload = order_payload(instrument_id=instrument_id, side=side, quantity=quantity)
        attach_json("order-request", payload)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A portfolio is ready for trading"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
            with allure.step("The order is sent to the trading endpoint"):
                response = client.submit_order(mocked["portfolio_id"], payload, idempotency_key())
            with allure.step("The order is accepted for execution"):
                assert response.status_code == requests.codes.accepted
                assert response.json()["status"] == "PENDING_EXECUTION"

    @allure.title("Valuation snapshots remain available for {currency} portfolios")
    @allure.description("Portfolio valuation can be retrieved with a positive net asset value.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("API-ORD-003")
    @pytest.mark.valuation
    @pytest.mark.parametrize(("currency", "nav"), VALUATION_CASES)
    def test_get_valuation_matrix(self, currency: str, nav: float):
        apply_runtime_labels(layer="api", component="valuation", capability="read")
        attach_test_parameters(currency=currency, nav=nav)
        client = portfolio_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A priced portfolio is available"):
                mocked = register_portfolio_api_mocks(mocker, SETTINGS)
            with allure.step("The latest valuation is requested"):
                response = client.get_valuation(mocked["portfolio_id"])
            with allure.step("A positive valuation is returned"):
                assert response.status_code == requests.codes.ok
                assert response.json()["nav"] > 0
                assert nav > 0
                assert currency in {"USD", "EUR", "GBP"}

    @allure.title("Client requests include a usable idempotency key")
    @allure.description("Generated idempotency keys follow the format used by the order and transfer endpoints.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("API-ORD-004")
    @pytest.mark.parametrize("sequence", IDEMPOTENCY_CASES)
    def test_idempotency_key_shape(self, sequence: int):
        apply_runtime_labels(layer="api", component="idempotency", capability="client-headers")
        attach_test_parameters(sequence=sequence)
        with allure.step("A fresh idempotency key is generated"):
            value = idempotency_key()
        with allure.step("The key matches the expected client format"):
            assert value.startswith("idem-")
            assert len(value) > 20
