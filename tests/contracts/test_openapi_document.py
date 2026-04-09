from __future__ import annotations

import allure
import pytest

from tests.helpers.allure_scenarios import (
    apply_runtime_labels,
    attach_test_parameters,
)
from tests.helpers.openapi import load_openapi_document
from tests.helpers.runtime import ensure_allure_metadata, get_project_root, get_settings

SETTINGS = get_settings()
ensure_allure_metadata(SETTINGS)
PORTFOLIO_OPENAPI = load_openapi_document(get_project_root() / "openapi" / "user-portfolio.yaml")
PORTFOLIO_PATHS = PORTFOLIO_OPENAPI["paths"]
EXPECTED_TAGS = {"Portfolios", "Transfers", "Orders", "Valuation", "Activities"}
PATH_TO_METHODS = {
    "/portfolios": ["post"],
    "/portfolios/{portfolio_id}": ["get"],
    "/portfolios/{portfolio_id}/cash-transfers": ["post"],
    "/portfolios/{portfolio_id}/orders": ["post"],
    "/portfolios/{portfolio_id}/positions": ["get"],
    "/portfolios/{portfolio_id}/valuation": ["get"],
    "/portfolios/{portfolio_id}/rebalance": ["post"],
    "/portfolios/{portfolio_id}/activities": ["get"],
}


@pytest.mark.contract
@allure.parent_suite("Portfolio Service")
@allure.suite("Contract")
@allure.sub_suite("OpenAPI Structure")
@allure.epic("Portfolio Service")
@allure.feature("OpenAPI Contract")
@allure.story("The contract document is structurally complete")
@allure.tag("contract", "openapi", "schema-governance")
@allure.label("layer", "contract")
@allure.label("service", "user-portfolio")
class TestOpenApiDocument:
    @allure.title("OpenAPI document exposes version, info, paths, and components")
    @allure.description("The contract exposes the core sections needed for validation and governance.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("CONTRACT-001")
    def test_contract_has_required_top_level_sections(self):
        apply_runtime_labels(layer="contract", component="openapi", capability="document-shape")
        with allure.step("Verify top-level keys in the contract"):
            assert PORTFOLIO_OPENAPI["openapi"].startswith("3.")
            assert "info" in PORTFOLIO_OPENAPI
            assert "paths" in PORTFOLIO_OPENAPI
            assert "components" in PORTFOLIO_OPENAPI

    @allure.title("Core path {path} is present in the contract")
    @allure.description("Each core portfolio capability is documented in the contract.")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id("CONTRACT-002")
    @pytest.mark.parametrize("path", list(PATH_TO_METHODS))
    def test_core_paths_exist(self, path: str):
        apply_runtime_labels(layer="contract", component="openapi", capability="path-coverage")
        attach_test_parameters(path=path)
        with allure.step(f"Assert that {path} exists in the path map"):
            assert path in PORTFOLIO_PATHS

    @allure.title("Path {path} declares method {method}")
    @allure.description("Each path exposes the methods supported by the service.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("CONTRACT-003")
    @pytest.mark.parametrize(
        ("path", "method"),
        [(path, method) for path, methods in PATH_TO_METHODS.items() for method in methods],
    )
    def test_path_method_exists(self, path: str, method: str):
        apply_runtime_labels(layer="contract", component="openapi", capability="method-coverage")
        attach_test_parameters(path=path, method=method)
        with allure.step(f"Assert that {method.upper()} is defined for {path}"):
            assert method in PORTFOLIO_PATHS[path]

    @allure.title("Operation {path} {method} has a stable operationId")
    @allure.description("Every operation has an operation identifier for contract-driven tooling.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("CONTRACT-004")
    @pytest.mark.parametrize(
        ("path", "method"),
        [(path, method) for path, methods in PATH_TO_METHODS.items() for method in methods],
    )
    def test_operation_ids_are_declared(self, path: str, method: str):
        apply_runtime_labels(layer="contract", component="openapi", capability="operation-id")
        with allure.step("Read the documented operation block"):
            operation = PORTFOLIO_PATHS[path][method]
        with allure.step("Validate the operationId format"):
            assert operation["operationId"]
            assert operation["operationId"][0].islower()

    @allure.title("Contract defines all expected business tags")
    @allure.description("The tag registry reflects the main functional areas of the service.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("CONTRACT-005")
    def test_expected_tags_are_registered(self):
        apply_runtime_labels(layer="contract", component="openapi", capability="tags")
        tags = {item["name"] for item in PORTFOLIO_OPENAPI["tags"]}
        with allure.step("Compare registered tags with expected business capabilities"):
            assert EXPECTED_TAGS <= tags

    @allure.title("Operation {path} {method} has at least one response code")
    @allure.description("Each operation declares at least one documented response.")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.id("CONTRACT-006")
    @pytest.mark.parametrize(
        ("path", "method"),
        [(path, method) for path, methods in PATH_TO_METHODS.items() for method in methods],
    )
    def test_operations_have_documented_responses(self, path: str, method: str):
        apply_runtime_labels(layer="contract", component="openapi", capability="responses")
        operation = PORTFOLIO_PATHS[path][method]
        with allure.step("Assert at least one response code is documented"):
            assert operation["responses"]

    @allure.title("Server URL is declared as a sandbox-like endpoint")
    @allure.description("The contract points to a sandbox-style endpoint instead of localhost.")
    @allure.severity(allure.severity_level.MINOR)
    @allure.id("CONTRACT-007")
    def test_server_url_is_non_local(self):
        apply_runtime_labels(layer="contract", component="openapi", capability="servers")
        server_url = PORTFOLIO_OPENAPI["servers"][0]["url"]
        with allure.step("Verify the server URL does not use localhost"):
            assert server_url.startswith("https://")
            assert "localhost" not in server_url
