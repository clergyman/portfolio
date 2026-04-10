from __future__ import annotations

import pytest
import requests
import responses

from tests.helpers.runtime import (
    mocked_petstore_api,
    petstore_api_client,
    require_live_sandbox,
)


@pytest.mark.smoke
class TestSwaggerPetstoreSmoke:
    def test_find_available_pets(self):
        client = petstore_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked_petstore_api(mocker)
            response = client.find_available_pets()

        assert response.status_code == requests.codes.ok
        assert isinstance(response.json(), list)
        assert response.json()[0]["status"] == "available"

    def test_store_inventory(self):
        client = petstore_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked_petstore_api(mocker)
            response = client.get_inventory()

        assert response.status_code == requests.codes.ok
        assert isinstance(response.json(), list)

    def test_missing_order(self):
        client = petstore_api_client()
        with responses.RequestsMock(assert_all_requests_are_fired=False) as mocker:
            mocked_petstore_api(mocker)
            response = client.get_order(order_id=999999999)

        assert response.status_code == requests.codes.not_found


@pytest.mark.live
class TestSwaggerPetstoreLive:
    def test_live_inventory(self):
        require_live_sandbox()
        response = petstore_api_client().get_inventory()

        assert response.status_code == requests.codes.ok
