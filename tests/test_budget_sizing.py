import json
import math
from pathlib import Path

import pytest

from delta_model.budget_sizing import (
    BUDGET_TRANSMISSION_CANDIDATES,
    assess_budget_operating_point,
    budget_performance_envelope_document,
    budget_transmission,
    screen_proxy_trace,
)
from delta_model.design_profiles import BUDGET_DEMONSTRATOR_PROFILE
from delta_model.drive_sizing import (
    DriveTransmission,
    TransmissionInertiaModel,
    calculate_refined_drive_load,
)
from delta_model.dynamics import DynamicMassCase, evaluate_dynamic_case
from delta_model.trajectory import generate_trajectory
from delta_model.transmission import solve_open_belt_geometry


def test_budget_belt_geometries_reconstruct_lengths_and_keep_six_teeth_in_mesh() -> None:
    for candidate in BUDGET_TRANSMISSION_CANDIDATES:
        geometry = solve_open_belt_geometry(candidate.belt)
        assert geometry.reconstructed_pitch_length_m == pytest.approx(
            candidate.belt.belt_pitch_length_m, abs=1e-9
        )
        assert geometry.small_teeth_in_mesh >= 6.0


def test_zero_transmission_inertia_reproduces_external_and_rotor_equation() -> None:
    trajectory = generate_trajectory(sample_period_s=0.010)
    dynamic = evaluate_dynamic_case(
        trajectory,
        DynamicMassCase("test", 0.3, 0.25, 0.2, 0.3),
    )
    zero = TransmissionInertiaModel(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    transmission = DriveTransmission(3.0, 0.85, 0.01, zero)
    rotor = BUDGET_DEMONSTRATOR_PROFILE.motor.rotor_inertia_kg_m2
    trace = calculate_refined_drive_load(
        trajectory, dynamic, rotor_inertia_kg_m2=rotor, transmission=transmission
    )
    index = next(
        index
        for index, sample in enumerate(trajectory.samples)
        if abs(sample.joint_accelerations.theta_1_rad_s2) > 1.0
    )
    acceleration = trajectory.samples[index].joint_accelerations.theta_1_rad_s2
    expected = dynamic.torques_nm[index][0] / (3.0 * 0.85) + rotor * 3.0 * acceleration
    assert trace.motor_torques_nm[index][0] == pytest.approx(expected, abs=1e-12)


def test_positive_input_inertia_changes_torque_in_acceleration_direction() -> None:
    trajectory = generate_trajectory(sample_period_s=0.010)
    dynamic = evaluate_dynamic_case(
        trajectory,
        DynamicMassCase("test", 0.3, 0.25, 0.2, 0.3),
    )
    base = budget_transmission(BUDGET_TRANSMISSION_CANDIDATES[0])
    increased = DriveTransmission(
        base.ratio,
        base.efficiency,
        base.small_pulley_pitch_radius_m,
        TransmissionInertiaModel(
            base.inertia.small_pulley_kg_m2 + 1e-4,
            base.inertia.input_shaft_kg_m2,
            base.inertia.coupling_kg_m2,
            base.inertia.belt_at_input_kg_m2,
            base.inertia.large_pulley_kg_m2,
            base.inertia.bushing_kg_m2,
            base.inertia.output_shaft_kg_m2,
        ),
    )
    rotor = BUDGET_DEMONSTRATOR_PROFILE.motor.rotor_inertia_kg_m2
    base_trace = calculate_refined_drive_load(
        trajectory, dynamic, rotor_inertia_kg_m2=rotor, transmission=base
    )
    increased_trace = calculate_refined_drive_load(
        trajectory, dynamic, rotor_inertia_kg_m2=rotor, transmission=increased
    )
    index = next(
        index
        for index, sample in enumerate(trajectory.samples)
        if abs(sample.joint_accelerations.theta_1_rad_s2) > 1.0
    )
    acceleration = trajectory.samples[index].joint_accelerations.theta_1_rad_s2
    torque_change = (
        increased_trace.motor_torques_nm[index][0]
        - base_trace.motor_torques_nm[index][0]
    )
    assert math.copysign(1.0, torque_change) == math.copysign(1.0, acceleration)


def test_constructed_over_torque_and_over_speed_samples_are_rejected() -> None:
    over_torque = screen_proxy_trace(((3.0, 0.0, 0.0),), ((0.0, 0.0, 0.0),))
    speed_rad_s = 1600.0 * 2.0 * math.pi / 60.0
    over_speed = screen_proxy_trace(((0.1, 0.0, 0.0),), ((speed_rad_s, 0.0, 0.0),))
    assert over_torque.worst_curve_utilization > 1.0
    assert over_speed.speed_evidence_exceeded


def test_catalogue_candidate_has_a_proxy_supported_half_kilogram_point() -> None:
    result = assess_budget_operating_point(
        BUDGET_TRANSMISSION_CANDIDATES[0], payload_kg=0.5, cycle_duration_s=1.5
    )
    assert result.status == "not_rejected_by_proxy"
    assert result.worst_curve_utilization == pytest.approx(0.852963138085264)


def test_budget_report_is_finite_deterministic_and_matches_artifact() -> None:
    document = budget_performance_envelope_document()
    encoded = json.dumps(document, allow_nan=False, sort_keys=True)
    committed = json.loads(
        (Path(__file__).parents[1] / "artifacts/budget_performance_envelope.json").read_text()
    )
    assert json.loads(encoded) == committed
