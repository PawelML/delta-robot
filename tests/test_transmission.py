import json
import math
from pathlib import Path
from typing import cast

import pytest
from hypothesis import given
from hypothesis import strategies as st

from delta_model.drive_sizing import LEADSHINE_ISV2_RS6040V48G, assess_refined_drive
from delta_model.dynamics import CONSERVATIVE_MASS_CASE, evaluate_dynamic_case
from delta_model.trajectory import generate_trajectory
from delta_model.transmission import (
    VARIANTS,
    BeltCandidate,
    inertia_from_wr2_lb_ft2,
    interpolate_selected_belt_capacity_w,
    open_belt_length_m,
    screen_candidate,
    selected_operating_point,
    shaft_screen,
    solve_open_belt_geometry,
    transmission_document,
)


def _document() -> dict[str, object]:
    trajectory = generate_trajectory()
    dynamic = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    assessment = assess_refined_drive(trajectory, dynamic, LEADSHINE_ISV2_RS6040V48G)
    peak_design_belt_torque = (
        max(axis.peak_belt_tension_difference_n for axis in assessment.axes)
        * (18 * 0.005 / (2.0 * math.pi))
        * assessment.design_factor
    )
    return transmission_document(
        maximum_motor_speed_rpm=assessment.maximum_motor_speed_rpm,
        peak_design_transmitted_torque_nm=peak_design_belt_torque,
        maximum_trajectory_belt_power_w=assessment.maximum_belt_power_w,
    )


def test_selected_geometry_matches_independent_hand_values() -> None:
    geometry = solve_open_belt_geometry(VARIANTS[1])

    assert VARIANTS[1].ratio == pytest.approx(5.0, abs=1e-12)
    assert geometry.centre_distance_m == pytest.approx(0.15436686875740537)
    assert geometry.reconstructed_pitch_length_m == pytest.approx(0.600, abs=1e-12)
    assert geometry.small_wrap_angle_deg == pytest.approx(136.4248719739229)
    assert geometry.small_teeth_in_mesh == pytest.approx(6.821243598696146)


def test_catalogue_inertias_are_converted_as_mass_moments() -> None:
    assert inertia_from_wr2_lb_ft2(0.000097) == pytest.approx(4.0875906797e-6)
    assert inertia_from_wr2_lb_ft2(0.1358) == pytest.approx(0.00572262695158)


def test_selected_operating_point_passes_published_power_screen() -> None:
    point = selected_operating_point(
        maximum_motor_speed_rpm=330.48,
        peak_design_transmitted_torque_nm=2.401,
        maximum_trajectory_belt_power_w=42.719,
    )

    assert point.belt_speed_m_s == pytest.approx(0.49572)
    assert point.capacity_status == "passes"
    assert point.capacity_utilization < 0.3
    assert point.conservative_radial_load_n > 350.0


def test_only_catalogue_backed_variant_is_recommended() -> None:
    screens = tuple(screen_candidate(candidate) for candidate in VARIANTS)

    assert [screen.status for screen in screens] == ["rejected", "recommended", "rejected"]
    assert "no_applicable_published_power_rating" in screens[0].reasons


def test_fewer_than_six_teeth_in_mesh_is_rejected() -> None:
    candidate = BeltCandidate(
        candidate_id="bad_mesh",
        small_teeth=12,
        large_teeth=60,
        belt_pitch_length_m=0.300,
        belt_width_m=0.015,
        small_pulley_catalogue="test",
        large_pulley_catalogue="test",
        published_rating_available=True,
        published_stock_pair=True,
    )

    screen = screen_candidate(candidate)

    assert screen.status == "rejected"
    assert "fewer_than_six_small_pulley_teeth_in_mesh" in screen.reasons


@given(st.floats(min_value=0.08, max_value=0.5, allow_nan=False, allow_infinity=False))
def test_open_belt_solution_round_trips_pitch_length(extra_length_m: float) -> None:
    small = 18 * 0.005 / math.pi
    large = 90 * 0.005 / math.pi
    minimum = math.pi * (large + small) / 2.0 + math.sqrt(2.0) * (large - small)
    candidate = BeltCandidate(
        candidate_id="property",
        small_teeth=18,
        large_teeth=90,
        belt_pitch_length_m=minimum + extra_length_m,
        belt_width_m=0.015,
        small_pulley_catalogue=None,
        large_pulley_catalogue=None,
        published_rating_available=False,
        published_stock_pair=False,
    )
    geometry = solve_open_belt_geometry(candidate)

    assert open_belt_length_m(
        geometry.centre_distance_m,
        geometry.small_pitch_diameter_m,
        geometry.large_pitch_diameter_m,
    ) == pytest.approx(candidate.belt_pitch_length_m, abs=1e-12)


@pytest.mark.parametrize("speed", [299.999, 400.001, math.inf, math.nan])
def test_capacity_interpolation_rejects_unsupported_speed(speed: float) -> None:
    with pytest.raises(ValueError, match=r"300\.\.400"):
        interpolate_selected_belt_capacity_w(speed)


def test_shaft_screen_rejects_non_physical_inputs() -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        shaft_screen(
            diameter_m=0.0,
            bearing_span_m=0.05,
            radial_load_n=300.0,
            transmitted_torque_nm=2.0,
        )


def test_transmission_report_matches_committed_artifact() -> None:
    document = _document()
    artifact_path = Path(__file__).resolve().parents[1] / "artifacts/p1_transmission_selection.json"
    committed = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert json.loads(json.dumps(document)) == committed
    recommendation = cast(dict[str, object], document["recommendation"])
    assert recommendation["ratio"] == 5.0
    operating = cast(dict[str, object], document["operating_point"])
    assert operating["capacity_status"] == "passes"
