from __future__ import annotations

from uuid import uuid4

import pytest

from tests.helpers.clients import PetstoreApiClient, PortfolioApiClient, build_session


@pytest.fixture(scope="function")
def correlation_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="function", autouse=True)
def attach_correlation_label(correlation_id: str):
    import allure

    allure.dynamic.label("correlation_id", correlation_id)


@pytest.fixture(scope="function")
def portfolio_api_client(settings, auth_token_customer: str, correlation_id: str) -> PortfolioApiClient:
    session = build_session(token=auth_token_customer, correlation_id=correlation_id)
    return PortfolioApiClient(base_url=settings.portfolio_api_base_url, session=session)


@pytest.fixture(scope="function")
def advisor_api_client(settings, auth_token_advisor: str, correlation_id: str) -> PortfolioApiClient:
    session = build_session(token=auth_token_advisor, correlation_id=correlation_id)
    return PortfolioApiClient(base_url=settings.portfolio_api_base_url, session=session)


@pytest.fixture(scope="function")
def petstore_api_client(settings, correlation_id: str) -> PetstoreApiClient:
    session = build_session(correlation_id=correlation_id)
    return PetstoreApiClient(base_url=settings.public_sandbox_base_url, session=session)
