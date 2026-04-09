from __future__ import annotations

import allure
import pytest
import requests


@pytest.mark.smoke
@allure.epic("External Sandbox")
@allure.feature("Swagger Petstore v3")
class TestSwaggerPetstoreSmoke:
    @allure.story("Available pets can be queried from a Petstore-shaped API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_find_available_pets(self, petstore_api_client, mocked_petstore_api):
        with allure.step("Request the list of available pets"):
            response = petstore_api_client.find_available_pets()

            assert response.status_code == requests.codes.ok
            assert isinstance(response.json(), list)
            assert response.json()[0]["status"] == "available"

    @allure.story("Inventory is exposed as a key-value mapping")
    @allure.severity(allure.severity_level.NORMAL)
    def test_store_inventory(self, petstore_api_client, mocked_petstore_api):
        with allure.step("Request the store inventory summary"):
            response = petstore_api_client.get_inventory()

            assert response.status_code == requests.codes.ok
            assert isinstance(response.json(), dict)

    @allure.story("Unknown orders return a documented not-found style response")
    @allure.severity(allure.severity_level.MINOR)
    def test_missing_order(self, petstore_api_client, mocked_petstore_api):
        with allure.step("Request an order that does not exist"):
            response = petstore_api_client.get_order(order_id=999999999)

            assert response.status_code == requests.codes.not_found


@pytest.mark.live
@allure.epic("External Sandbox")
@allure.feature("Swagger Petstore v3")
class TestSwaggerPetstoreLive:
    @allure.story("The public sandbox can be reached when live checks are enabled")
    def test_live_inventory(self, petstore_api_client, require_live_sandbox):
        with allure.step("Request inventory from the live Petstore sandbox"):
            response = petstore_api_client.get_inventory()

            assert response.status_code == requests.codes.ok
