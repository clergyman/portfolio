from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass(frozen=True)
class TestSettings:
    project_root: Path
    portfolio_api_base_url: str
    public_sandbox_base_url: str
    test_environment: str


def load_settings(project_root: Path) -> TestSettings:
    return TestSettings(
        project_root=project_root,
        portfolio_api_base_url=getenv(
            "PORTFOLIO_API_BASE_URL", "https://portfolio-api.sandbox.allyre.example"
        ).rstrip("/"),
        public_sandbox_base_url=getenv(
            "PUBLIC_SANDBOX_BASE_URL", "https://petstore3.swagger.io/api/v3"
        ).rstrip("/"),
        test_environment=getenv("TEST_ENVIRONMENT", "local"),
    )
