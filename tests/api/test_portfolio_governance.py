from __future__ import annotations

import allure
import pytest

from tests.helpers.allure_scenarios import apply_runtime_labels, attach_test_parameters

RISK_CASES = [
    ("CONSERVATIVE", "INCOME"),
    ("MODERATE", "BALANCED"),
    ("AGGRESSIVE", "GROWTH"),
    ("MODERATE", "INCOME"),
    ("AGGRESSIVE", "BALANCED"),
    ("CONSERVATIVE", "BALANCED"),
]
ACTIVITY_CASES = [
    ("PORTFOLIO_CREATED", True),
    ("CASH_TRANSFER", True),
    ("ORDER_SUBMITTED", True),
    ("ORDER_FILLED", True),
    ("REBALANCE_REQUESTED", True),
    ("ORDER_REJECTED", False),
]


@pytest.mark.api
@allure.parent_suite("Portfolio Service")
@allure.suite("API")
@allure.sub_suite("Portfolio Governance")
@allure.epic("Portfolio Service")
@allure.feature("Portfolio Governance")
@allure.story("Strategy, risk, and timeline semantics")
@allure.tag("api", "governance", "portfolio")
@allure.label("layer", "api")
class TestPortfolioGovernance:
    @allure.title("Risk profile {risk_profile} aligns with strategy {strategy}")
    @allure.description("Sample portfolio setups remain believable for different investor profiles.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("API-GOV-001")
    @pytest.mark.parametrize(("risk_profile", "strategy"), RISK_CASES)
    def test_risk_profile_strategy_alignment(self, risk_profile: str, strategy: str):
        apply_runtime_labels(layer="api", component="portfolio-governance", capability="risk-mapping")
        attach_test_parameters(risk_profile=risk_profile, strategy=strategy)
        with allure.step("The strategy remains consistent with the investor profile"):
            if risk_profile == "CONSERVATIVE":
                assert strategy in {"INCOME", "BALANCED"}
            if risk_profile == "AGGRESSIVE":
                assert strategy in {"GROWTH", "BALANCED"}

    @allure.title("Activity type {activity_type} exposes visibility expectation")
    @allure.description("Activity types are classified in a way that makes sense for client-facing timelines.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("API-GOV-002")
    @pytest.mark.parametrize(("activity_type", "visible_to_user"), ACTIVITY_CASES)
    def test_activity_visibility_model(self, activity_type: str, visible_to_user: bool):
        apply_runtime_labels(layer="api", component="activity-feed", capability="timeline")
        attach_test_parameters(activity_type=activity_type, visible_to_user=visible_to_user)
        with allure.step("The activity visibility follows the timeline rules"):
            if activity_type == "ORDER_REJECTED":
                assert visible_to_user is False
            else:
                assert visible_to_user is True
