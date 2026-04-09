from __future__ import annotations

from typing import Any

import pytest

from tests.helpers.openapi import load_openapi_document


@pytest.fixture(scope="session")
def portfolio_openapi(settings) -> dict[str, Any]:
    return load_openapi_document(settings.project_root / "openapi" / "user-portfolio.yaml")


@pytest.fixture(scope="module")
def portfolio_paths(portfolio_openapi: dict[str, Any]) -> dict[str, Any]:
    return portfolio_openapi["paths"]
