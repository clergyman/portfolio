from __future__ import annotations

import pytest


@pytest.fixture(scope="session")
def auth_token_customer() -> str:
    return "customer-token-demo"


@pytest.fixture(scope="session")
def auth_token_advisor() -> str:
    return "advisor-token-demo"


@pytest.fixture(scope="class", params=["customer", "advisor"])
def api_actor_role(request) -> str:
    return request.param
