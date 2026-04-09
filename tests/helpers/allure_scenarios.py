from __future__ import annotations

import json
import os
import random
import time
from typing import Any

import allure
import pytest


def apply_runtime_labels(*, layer: str, component: str, capability: str, owner: str = "qa-platform") -> None:
    allure.dynamic.label("layer", layer)
    allure.dynamic.label("component", component)
    allure.dynamic.label("capability", capability)
    allure.dynamic.label("owner", owner)
    allure.dynamic.label("microservice", "user-portfolio")
    allure.dynamic.tag(layer, component, capability, "offline")


def attach_json(name: str, payload: Any) -> None:
    allure.attach(
        json.dumps(payload, indent=2, sort_keys=True),
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )


def attach_text(name: str, value: str) -> None:
    allure.attach(value, name=name, attachment_type=allure.attachment_type.TEXT)


def attach_expected_result(text: str) -> None:
    attach_text("expected-result", text)


def attach_business_context(text: str) -> None:
    attach_text("business-context", text)


def attach_test_parameters(**kwargs: Any) -> None:
    for key, value in kwargs.items():
        allure.dynamic.parameter(key, value)


def slow_e2e_pause(multiplier: float = 1.0) -> None:
    time.sleep(0.03 * multiplier)


def maybe_fail_randomly(*, probability: float = 0.2, reason: str = "Intentional flaky test") -> None:
    if os.getenv("ENABLE_RANDOM_FLAKES", "1") != "1":
        return
    if random.random() < probability:
        pytest.fail(reason)
