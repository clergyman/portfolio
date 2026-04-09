from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.settings import TestSettings, load_settings


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def settings(project_root: Path) -> TestSettings:
    return load_settings(project_root)
