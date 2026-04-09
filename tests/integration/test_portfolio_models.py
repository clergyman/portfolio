from __future__ import annotations

import pytest

from tests.helpers.runtime import market_snapshot, seeded_instruments


@pytest.mark.integration
class TestPortfolioIntegrationModel:
    def test_seeded_instruments_cover_multiple_asset_classes(self):
        asset_classes = {item["asset_class"] for item in seeded_instruments()}
        assert {"ETF", "BOND"} <= asset_classes

    @pytest.mark.valuation
    def test_package_snapshot_contains_reference_prices(self):
        snapshot = market_snapshot()
        assert snapshot["ETF-ACWI"]["price"] > 0
        assert snapshot["ETF-BND"]["fx_rate"] == 1.0
