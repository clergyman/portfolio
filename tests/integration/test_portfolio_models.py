from __future__ import annotations

import allure
import pytest

from tests.helpers.runtime import ensure_allure_metadata, market_snapshot, seeded_instruments

ensure_allure_metadata()


@pytest.mark.integration
@allure.epic("Portfolio Service")
@allure.feature("Integration Modeling")
class TestPortfolioIntegrationModel:
    @allure.story("Seeded instruments support valuation and rebalance flows")
    def test_seeded_instruments_cover_multiple_asset_classes(self):
        asset_classes = {item["asset_class"] for item in seeded_instruments()}
        assert {"ETF", "BOND"} <= asset_classes

    @allure.story("A package-wide market snapshot is stable for an entire test package")
    @pytest.mark.valuation
    def test_package_snapshot_contains_reference_prices(self):
        snapshot = market_snapshot()
        assert snapshot["ETF-ACWI"]["price"] > 0
        assert snapshot["ETF-BND"]["fx_rate"] == 1.0
