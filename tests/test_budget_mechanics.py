import json
import math
from pathlib import Path

import pytest

from delta_model.budget_mechanics import (
    GATES_5M_15_MIN_INSTALLATION_TENSION_N,
    MOTOR_DYNAMIC_RADIAL_LIMIT_N,
    budget_mechanical_closure_document,
    calculate_belt_radial_load,
    screen_output_bearings,
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


def test_faster_point_governs_the_belt_load_and_meets_provisional_screen() -> None:
    document = budget_mechanical_closure_document()
    faster = document["faster_operating_point"]
    assert isinstance(faster, dict)
    assert faster["performance_point"]["payload_kg"] == 0.30
    assert faster["performance_point"]["cycle_duration_s"] == 1.25
    assert faster["belt_load"]["resultant_radial_load_n"] == pytest.approx(245.49, abs=0.01)
    assert faster["shaft_screen"]["coupling_torque_factor"] == pytest.approx(1.41, abs=0.01)
    assert faster["passes_provisional_screen"] is True


def test_selected_output_bearings_have_capacity_and_speed_margin() -> None:
    screen = screen_output_bearings(
        belt_radial_load_n=234.41732472531334,
        maximum_output_speed_rpm=44.06334973430553,
    )
    assert screen.bearing_count == 2
    assert screen.bearing_span_m == pytest.approx(0.060)
    assert screen.belt_reaction_per_bearing_n == pytest.approx(
        screen.belt_radial_load_n / 2.0
    )
    assert screen.dynamic_rating_utilization < 0.10
    assert screen.static_safety_factor >= 3.0
    assert screen.speed_utilization < 0.10


def test_output_bearing_selection_is_exact_and_not_c3() -> None:
    document = budget_mechanical_closure_document()
    supported_output = document["supported_output"]
    assert isinstance(supported_output, dict)
    selected = supported_output["selected_bearing"]
    assert isinstance(selected, dict)
    assert selected["manufacturer"] == "SKF"
    assert selected["designation"] == "6001-2RSH"
    assert selected["internal_clearance"] == "CN (normal)"
    assert selected["bore_m"] == pytest.approx(0.012)
    assert selected["outside_diameter_m"] == pytest.approx(0.028)
    assert selected["width_m"] == pytest.approx(0.008)


def test_budget_mechanical_report_is_finite_deterministic_and_matches_artifact() -> None:
    document = budget_mechanical_closure_document()
    encoded = json.dumps(document, allow_nan=False, sort_keys=True)
    committed = json.loads(
        (Path(__file__).parents[1] / "artifacts/budget_mechanical_closure.json").read_text()
    )
    assert json.loads(encoded) == committed
