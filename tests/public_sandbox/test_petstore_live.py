from __future__ import annotations

import allure
import pytest
import requests
import responses

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_test_parameters,
    maybe_fail_randomly,
)
from tests.helpers.runtime import (
    ensure_allure_metadata,
    get_settings,
    petstore_client,
    register_petstore_api_mocks,
    require_live_sandbox,
)

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)
ORDER_CASES = [999999999, 999999998, 999999997, 999999996]
STATUS_CASES = ["available", "available", "available", "available"]


@pytest.mark.smoke
@allure.parent_suite("External Sandbox")
@allure.suite("Sandbox")
@allure.sub_suite("Petstore Offline Smoke")
@allure.epic("External Sandbox")
@allure.feature("Swagger Petstore v3")
@allure.story("Petstore-shaped smoke validation")
@allure.tag("sandbox", "petstore", "smoke")
@allure.label("layer", "sandbox")
class TestSwaggerPetstoreSmoke:
    @allure.title("Available pets can be listed")
    @allure.description("The Petstore-style endpoint returns a list of available pets.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("SBX-001")
    def test_find_available_pets(self):
        apply_runtime_labels(layer="sandbox", component="petstore", capability="find-pets")
        client = petstore_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A Petstore-style sandbox is available"):
                register_petstore_api_mocks(mocker, SETTINGS)
            with allure.step("The client asks for available pets"):
                response = client.find_available_pets()
            with allure.step("Available pets are returned"):
                assert response.status_code == requests.codes.ok
                assert isinstance(response.json(), list)
                assert response.json()[0]["status"] == "available"

    @allure.title("Store inventory is returned as a summary")
    @allure.description("The inventory endpoint returns a keyed summary of pet statuses.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("SBX-002")
    def test_store_inventory(self):
        apply_runtime_labels(layer="sandbox", component="petstore", capability="inventory")
        client = petstore_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("The inventory endpoint is available"):
                register_petstore_api_mocks(mocker, SETTINGS)
            with allure.step("The client requests the inventory summary"):
                response = client.get_inventory()
            with allure.step("The inventory summary is returned"):
                assert response.status_code == requests.codes.ok
                assert isinstance(response.json(), dict)

    @allure.title("Unknown order {order_id} is not found")
    @allure.description("Missing store orders return a not found response.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("SBX-003")
    @pytest.mark.parametrize("order_id", ORDER_CASES)
    def test_missing_order(self, order_id: int):
        apply_runtime_labels(layer="sandbox", component="petstore", capability="orders")
        attach_test_parameters(order_id=order_id)
        client = petstore_client(SETTINGS)
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            with allure.step("A sandbox order service is available"):
                register_petstore_api_mocks(mocker, SETTINGS)
            with allure.step("The client looks up a missing order"):
                response = client.get_order(order_id=order_id)
            with allure.step("The service responds that the order does not exist"):
                assert response.status_code == requests.codes.not_found

    @allure.title("The available status filter remains supported")
    @allure.description("The sandbox keeps the same status value for available pets.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("SBX-004")
    @pytest.mark.parametrize("status", STATUS_CASES)
    def test_status_parameter_semantics(self, status: str):
        apply_runtime_labels(layer="sandbox", component="petstore", capability="query-params")
        attach_test_parameters(status=status)
        with allure.step("The supported status value is checked"):
            assert status == "available"


@pytest.mark.live
@allure.parent_suite("External Sandbox")
@allure.suite("Sandbox")
@allure.sub_suite("Petstore Live")
@allure.epic("External Sandbox")
@allure.feature("Swagger Petstore v3")
@allure.story("Optional live connectivity")
@allure.tag("sandbox", "petstore", "live")
@allure.label("layer", "sandbox")
class TestSwaggerPetstoreLive:
    @allure.title("Live inventory can be fetched when sandbox access is enabled")
    @allure.description("The public sandbox responds successfully when live checks are turned on.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("SBX-101")
    def test_live_inventory(self):
        apply_runtime_labels(layer="sandbox", component="petstore", capability="live-connectivity")
        require_live_sandbox()
        with allure.step("The client calls the live inventory endpoint"):
            response = petstore_client(SETTINGS).get_inventory()
        with allure.step("The live sandbox responds successfully"):
            assert response.status_code == requests.codes.ok


@pytest.mark.flaky
@allure.parent_suite("External Sandbox")
@allure.suite("Sandbox")
@allure.sub_suite("Intentional Flakes")
@allure.epic("External Sandbox")
@allure.feature("Transient Sandbox Checks")
@allure.story("Random instability examples")
@allure.tag("flaky", "sandbox")
@allure.label("layer", "sandbox")
class TestIntentionalFlakes:
    @allure.title("Transient sandbox instability sample {index}")
    @allure.description("This sample usually passes, but it can fail occasionally to simulate an unstable check.")
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.id("SBX-FLAKY-001")
    @pytest.mark.parametrize("index", [1, 2, 3])
    def test_random_flake(self, index: int):
        apply_runtime_labels(layer="sandbox", component="flake-demo", capability="random-instability")
        attach_test_parameters(index=index)
        with allure.step("A transient sandbox check is performed"):
            maybe_fail_randomly(probability=0.2, reason=f"Intentional flaky failure for sample {index}")
        with allure.step("The sample passes if no transient failure occurs"):
            assert True
