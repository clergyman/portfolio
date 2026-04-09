from __future__ import annotations

import platform
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_allure_dirs(settings):
    settings.allure_results_dir.mkdir(parents=True, exist_ok=True)
    environment_file = settings.allure_results_dir / "environment.properties"
    environment_file.write_text(
        "\n".join(
            [
                f"TEST_ENVIRONMENT={settings.test_environment}",
                f"PORTFOLIO_API_BASE_URL={settings.portfolio_api_base_url}",
                f"PUBLIC_SANDBOX_BASE_URL={settings.public_sandbox_base_url}",
                f"PYTHON_VERSION={platform.python_version()}",
                f"PLATFORM={platform.platform()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    executor_file = settings.allure_results_dir / "executor.json"
    executor_file.write_text(
        (
            "{\n"
            '  "name": "pytest",\n'
            '  "type": "local",\n'
            '  "buildName": "portfolio-api-test-pack",\n'
            '  "buildUrl": "https://example.invalid/local-run",\n'
            f'  "reportName": "Portfolio API Test Pack on Python {platform.python_version()}"\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    categories_src = settings.project_root / "allure" / "categories.json"
    categories_dst = settings.allure_results_dir / "categories.json"
    categories_dst.write_text(categories_src.read_text(encoding="utf-8"), encoding="utf-8")
    yield


@pytest.fixture(scope="function")
def idempotency_key() -> str:
    return f"idem-{uuid4().hex}-{uuid4().hex[:12]}"


@pytest.fixture(scope="class")
def class_portfolio_context(portfolio_record_factory):
    return portfolio_record_factory()


@pytest.fixture(scope="module")
def module_dataset_path(settings) -> Path:
    return settings.project_root / "openapi" / "user-portfolio.yaml"
