import json
import math
from pathlib import Path

import pytest

from delta_model.budget_mechanics import (
    GATES_5M_15_MIN_INSTALLATION_TENSION_N,
    MOTOR_DYNAMIC_RADIAL_LIMIT_N,
    budget_mechanical_closure_document,
    calculate_belt_radial_load,
)


def test_equal_parallel_span_tensions_give_twice_one_span_tension() -> None:
    load = calculate_belt_radial_load(
        effective_tension_difference_n=0.0,
        installation_tension_per_span_n=60.0,
        span_included_angle_rad=0.0,
    )
    assert load.resultant_radial_load_n == pytest.approx(120.0)


def test_increasing_installation_tension_increases_radial_load() -> None:
    low = calculate_belt_radial_load(
        effective_tension_difference_n=100.0,
        installation_tension_per_span_n=30.0,
        span_included_angle_rad=math.radians(30.0),
    )
    high = calculate_belt_radial_load(
        effective_tension_difference_n=100.0,
        installation_tension_per_span_n=60.0,
        span_included_angle_rad=math.radians(30.0),
    )
    assert high.resultant_radial_load_n > low.resultant_radial_load_n


def test_selected_direct_layout_is_rejected_and_supported_layout_passes_screen() -> None:
    document = budget_mechanical_closure_document()
    direct = document["direct_motor_shaft"]
    supported = document["supported_input"]
    assert isinstance(direct, dict)
    assert isinstance(supported, dict)
    assert direct["peak_effective_tension_difference_n"] > MOTOR_DYNAMIC_RADIAL_LIMIT_N
    assert direct["status"] == "rejected"
    shaft = supported["shaft_screen"]
    assert isinstance(shaft, dict)
    assert shaft["yield_safety_factor"] >= 2.0
    assert shaft["bearing_rating_utilization"] < 0.10
    assert shaft["coupling_torque_factor"] >= 1.30
    performance = document["performance_point"]
    assert isinstance(performance, dict)
    assert performance["status"] == "not_rejected_by_proxy"
    assert document["status"] == "digital_screen_passed_physical_p1_pending"


def test_gates_tension_conversion_is_exactly_traceable() -> None:
    assert pytest.approx(13.5 * 4.4482216152605, abs=1e-12) == (
        GATES_5M_15_MIN_INSTALLATION_TENSION_N
    )


def test_budget_mechanical_report_is_finite_deterministic_and_matches_artifact() -> None:
    document = budget_mechanical_closure_document()
    encoded = json.dumps(document, allow_nan=False, sort_keys=True)
    committed = json.loads(
        (Path(__file__).parents[1] / "artifacts/budget_mechanical_closure.json").read_text()
    )
    assert json.loads(encoded) == committed
