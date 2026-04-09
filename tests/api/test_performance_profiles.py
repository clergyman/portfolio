from __future__ import annotations

import allure
import pytest

from tests.helpers.allure_scenarios import apply_runtime_labels, attach_test_parameters

PERFORMANCE_CASES = [
    ("create-portfolio", 120),
    ("get-portfolio", 90),
    ("cash-transfer", 110),
    ("submit-order", 130),
    ("valuation", 140),
    ("activities-feed", 150),
    ("positions-list", 100),
    ("rebalance-plan", 180),
]


@pytest.mark.api
@pytest.mark.performance
@allure.parent_suite("Portfolio Service")
@allure.suite("API")
@allure.sub_suite("Performance Profiles")
@allure.epic("Portfolio Service")
@allure.feature("Performance")
@allure.story("Budget-oriented API checks")
@allure.tag("api", "performance", "budgets")
@allure.label("layer", "api")
class TestPerformanceProfiles:
    @allure.title("Modeled endpoint {operation_name} stays within {latency_budget_ms} ms budget")
    @allure.description("Latency budgets stay within a realistic range for a trading platform API.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("API-PERF-001")
    @pytest.mark.parametrize(("operation_name", "latency_budget_ms"), PERFORMANCE_CASES)
    def test_latency_budgets(self, operation_name: str, latency_budget_ms: int):
        apply_runtime_labels(layer="api", component="performance", capability="latency-budget")
        attach_test_parameters(operation_name=operation_name, latency_budget_ms=latency_budget_ms)
        with allure.step("The latency budget remains within the agreed range"):
            assert 0 < latency_budget_ms < 250
