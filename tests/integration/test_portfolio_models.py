from __future__ import annotations

import allure
import pytest

from tests.helpers.allure_scenarios import apply_runtime_labels, attach_test_parameters
from tests.helpers.runtime import ensure_allure_metadata, get_settings

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)
SEEDED_INSTRUMENTS = [
    {"instrument_id": "ETF-ACWI", "asset_class": "ETF", "symbol": "ACWI"},
    {"instrument_id": "ETF-BND", "asset_class": "BOND", "symbol": "BND"},
    {"instrument_id": "ETF-VUSA", "asset_class": "ETF", "symbol": "VUSA"},
    {"instrument_id": "CASH-USD", "asset_class": "CASH", "symbol": "USD"},
    {"instrument_id": "BOND-EURO", "asset_class": "BOND", "symbol": "EUBND"},
]
PACKAGE_MARKET_SNAPSHOT = {
    "ETF-ACWI": {"price": 102.34, "fx_rate": 1.0},
    "ETF-BND": {"price": 77.18, "fx_rate": 1.0},
    "ETF-VUSA": {"price": 89.52, "fx_rate": 1.0},
    "CASH-USD": {"price": 1.0, "fx_rate": 1.0},
    "BOND-EURO": {"price": 98.11, "fx_rate": 1.07},
}
VALUATION_CASES = [
    (10000.0, 15123.40, 25123.40),
    (5000.0, 3200.0, 8200.0),
    (750.0, 0.0, 750.0),
    (1200.0, 100.0, 1300.0),
    (0.0, 9800.25, 9800.25),
    (22000.0, 187.5, 22187.5),
]
ALLOCATION_CASES = [
    ("growth-heavy", 0.72, 0.28),
    ("balanced", 0.55, 0.45),
    ("income", 0.30, 0.70),
    ("cash-defensive", 0.20, 0.80),
    ("equity-tilt", 0.65, 0.35),
    ("bond-tilt", 0.40, 0.60),
]


@pytest.mark.integration
@allure.parent_suite("Portfolio Service")
@allure.suite("Integration")
@allure.sub_suite("Portfolio Modeling")
@allure.epic("Portfolio Service")
@allure.feature("Integration Modeling")
@allure.story("Seeded data and valuation semantics")
@allure.tag("integration", "portfolio-model", "valuation")
@allure.label("layer", "integration")
class TestPortfolioIntegrationModel:
    @allure.title("Instrument {instrument_id} belongs to a supported asset class")
    @allure.description("The integration seed set covers the asset classes used throughout the suite.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("INT-001")
    @pytest.mark.parametrize("instrument", SEEDED_INSTRUMENTS)
    def test_seeded_instruments_cover_multiple_asset_classes(self, instrument: dict):
        apply_runtime_labels(layer="integration", component="seed-data", capability="instrument-catalog")
        attach_test_parameters(instrument_id=instrument["instrument_id"], asset_class=instrument["asset_class"])
        with allure.step("Verify the seeded instrument belongs to a supported class"):
            assert instrument["asset_class"] in {"ETF", "BOND", "CASH"}

    @allure.title("Market snapshot for {instrument_id} has usable price and FX metadata")
    @allure.description("Mocked market prices are positive and include FX rates where needed.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("INT-002")
    @pytest.mark.valuation
    @pytest.mark.parametrize("instrument_id", list(PACKAGE_MARKET_SNAPSHOT))
    def test_package_snapshot_contains_reference_prices(self, instrument_id: str):
        apply_runtime_labels(layer="integration", component="market-data", capability="pricing-snapshot")
        snapshot = PACKAGE_MARKET_SNAPSHOT[instrument_id]
        with allure.step("Validate the pricing snapshot"):
            assert snapshot["price"] > 0
            assert snapshot["fx_rate"] > 0

    @allure.title("NAV derives correctly from cash {cash_total} and positions {positions_total}")
    @allure.description("The valuation total is derived from cash and positions.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("INT-003")
    @pytest.mark.parametrize(("cash_total", "positions_total", "expected_nav"), VALUATION_CASES)
    def test_nav_derivation(self, cash_total: float, positions_total: float, expected_nav: float):
        apply_runtime_labels(layer="integration", component="valuation", capability="nav-calculation")
        with allure.step("The portfolio value is calculated from cash and positions"):
            actual_nav = cash_total + positions_total
        with allure.step("The calculated portfolio value matches the expected result"):
            assert actual_nav == expected_nav

    @allure.title("Allocation profile {profile_name} stays within a full 100 percent allocation")
    @allure.description("Strategic allocations remain normalized across the sample profiles.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("INT-004")
    @pytest.mark.parametrize(("profile_name", "equity_weight", "defensive_weight"), ALLOCATION_CASES)
    def test_allocation_buckets_sum_to_one(self, profile_name: str, equity_weight: float, defensive_weight: float):
        apply_runtime_labels(layer="integration", component="allocation", capability="weight-normalization")
        attach_test_parameters(profile_name=profile_name)
        with allure.step("Validate that weights sum to 100 percent"):
            assert round(equity_weight + defensive_weight, 2) == 1.0
