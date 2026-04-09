from __future__ import annotations

import allure
import pytest


@pytest.mark.integration
@allure.epic("Portfolio Service")
@allure.feature("Integration Modeling")
class TestPortfolioIntegrationModel:
    @allure.story("Seeded instruments support valuation and rebalance flows")
    def test_seeded_instruments_cover_multiple_asset_classes(self, seeded_instruments):
        asset_classes = {item["asset_class"] for item in seeded_instruments}
        assert {"ETF", "BOND"} <= asset_classes

    @allure.story("A package-wide market snapshot is stable for an entire test package")
    @pytest.mark.valuation
    def test_package_snapshot_contains_reference_prices(self, package_market_snapshot):
        assert package_market_snapshot["ETF-ACWI"]["price"] > 0
        assert package_market_snapshot["ETF-BND"]["fx_rate"] == 1.0
