import math
from dataclasses import replace

import pytest

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.design_geometry import SELECTED_GEOMETRY
from delta_model.differential_kinematics import (
    CartesianAcceleration,
    JointAccelerations,
    differential_kinematics,
)
from delta_model.drive_sizing import (
    INDUSTRIAL_REFERENCE_TRANSMISSION,
    LEADSHINE_ISV2_RS6040V48G,
    DriveTransmission,
    TransmissionInertiaModel,
    assess_motor_candidate,
    assess_refined_drive,
)
from delta_model.dynamics import (
    CONSERVATIVE_MASS_CASE,
    NOMINAL_MASS_CASE,
    DynamicMassCase,
    evaluate_dynamic_case,
    joint_effective_inertias_kg_m2,
    load_torques_for_state,
    platform_load_torques,
)
from delta_model.trajectory import generate_trajectory


def _zero_joint_acceleration() -> JointAccelerations:
    return JointAccelerations(0.0, 0.0, 0.0)


def test_zero_mass_produces_zero_torque() -> None:
    differential = differential_kinematics(
        SELECTED_GEOMETRY,
        CartesianPosition(0.0, 0.0, -0.347),
        AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
    )
    zero_mass = DynamicMassCase("zero", 0.0, 0.0, 0.0, 0.0)

    torques = load_torques_for_state(
        differential,
        CartesianAcceleration(10.0, -3.0, 5.0),
        JointAccelerations(20.0, -30.0, 40.0),
        zero_mass,
    )

    assert torques == pytest.approx((0.0, 0.0, 0.0), abs=1e-15)


def test_stationary_center_gravity_torques_are_symmetric() -> None:
    differential = differential_kinematics(
        SELECTED_GEOMETRY,
        CartesianPosition(0.0, 0.0, -0.347),
        AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
    )

    torques = load_torques_for_state(
        differential,
        CartesianAcceleration(0.0, 0.0, 0.0),
        _zero_joint_acceleration(),
        NOMINAL_MASS_CASE,
    )

    assert torques[0] == pytest.approx(torques[1], abs=1e-12)
    assert torques[0] == pytest.approx(torques[2], abs=1e-12)


def test_platform_virtual_work_identity() -> None:
    sample = generate_trajectory().samples[250]
    force = (3.0, -2.0, 8.0)
    torques = platform_load_torques(sample.differential, force)
    rates = sample.joint_rates
    velocity = sample.cartesian.velocity

    joint_power = (
        torques[0] * rates.theta_1_rad_s
        + torques[1] * rates.theta_2_rad_s
        + torques[2] * rates.theta_3_rad_s
    )
    cartesian_power = (
        force[0] * velocity.x_m_s
        + force[1] * velocity.y_m_s
        + force[2] * velocity.z_m_s
    )
    assert joint_power == pytest.approx(cartesian_power, abs=1e-10)


def test_doubling_all_masses_doubles_torque() -> None:
    sample = generate_trajectory().samples[275]
    doubled = replace(
        NOMINAL_MASS_CASE,
        case_id="double",
        payload_kg=2.0 * NOMINAL_MASS_CASE.payload_kg,
        platform_tooling_kg=2.0 * NOMINAL_MASS_CASE.platform_tooling_kg,
        upper_arm_each_kg=2.0 * NOMINAL_MASS_CASE.upper_arm_each_kg,
        lower_assemblies_total_kg=2.0 * NOMINAL_MASS_CASE.lower_assemblies_total_kg,
    )

    base = load_torques_for_state(
        sample.differential,
        sample.cartesian.acceleration,
        sample.joint_accelerations,
        NOMINAL_MASS_CASE,
    )
    scaled = load_torques_for_state(
        sample.differential,
        sample.cartesian.acceleration,
        sample.joint_accelerations,
        doubled,
    )

    assert scaled == pytest.approx(tuple(2.0 * value for value in base), abs=1e-12)


def test_peak_torque_is_not_below_rms() -> None:
    result = evaluate_dynamic_case(generate_trajectory(), NOMINAL_MASS_CASE)

    assert len(result.torques_nm) == 1001
    for axis in result.axes:
        assert math.isfinite(axis.peak_abs_torque_nm)
        assert axis.peak_abs_torque_nm >= axis.rms_torque_nm >= 0.0


def test_leadshine_candidate_passes_conservative_case_with_rotor_inertia() -> None:
    trajectory = generate_trajectory()
    result = evaluate_dynamic_case(trajectory, NOMINAL_MASS_CASE)
    conservative = replace(
        NOMINAL_MASS_CASE,
        case_id="conservative",
        payload_kg=0.5,
        platform_tooling_kg=0.3,
        upper_arm_each_kg=0.25,
        lower_assemblies_total_kg=0.36,
    )
    conservative_result = evaluate_dynamic_case(trajectory, conservative)
    assert max(axis.peak_abs_torque_nm for axis in conservative_result.axes) > max(
        axis.peak_abs_torque_nm for axis in result.axes
    )

    assessment = assess_motor_candidate(
        trajectory,
        conservative_result,
        LEADSHINE_ISV2_RS6040V48G,
        ratio=INDUSTRIAL_REFERENCE_TRANSMISSION.ratio,
        efficiency=INDUSTRIAL_REFERENCE_TRANSMISSION.efficiency,
    )

    assert assessment.passes
    assert assessment.maximum_motor_speed_rpm == pytest.approx(330.4751230072913)
    assert max(axis.required_peak_torque_nm for axis in assessment.axes) == pytest.approx(
        2.401083715716091
    )
    assert max(axis.required_rms_torque_nm for axis in assessment.axes) == pytest.approx(
        1.0264640660097457
    )


def test_zero_transmission_inertia_reproduces_legacy_candidate_assessment() -> None:
    trajectory = generate_trajectory()
    result = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    legacy = assess_motor_candidate(
        trajectory,
        result,
        LEADSHINE_ISV2_RS6040V48G,
        ratio=INDUSTRIAL_REFERENCE_TRANSMISSION.ratio,
        efficiency=INDUSTRIAL_REFERENCE_TRANSMISSION.efficiency,
    )
    zero_inertia = TransmissionInertiaModel(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    zero = DriveTransmission(
        ratio=INDUSTRIAL_REFERENCE_TRANSMISSION.ratio,
        efficiency=INDUSTRIAL_REFERENCE_TRANSMISSION.efficiency,
        small_pulley_pitch_radius_m=(
            INDUSTRIAL_REFERENCE_TRANSMISSION.small_pulley_pitch_radius_m
        ),
        inertia=zero_inertia,
    )

    refined = assess_refined_drive(
        trajectory,
        result,
        LEADSHINE_ISV2_RS6040V48G,
        zero,
    )

    for legacy_axis, refined_axis in zip(legacy.axes, refined.axes, strict=True):
        assert refined_axis.required_peak_torque_nm == pytest.approx(
            legacy_axis.required_peak_torque_nm, abs=1e-12
        )
        assert refined_axis.required_rms_torque_nm == pytest.approx(
            legacy_axis.required_rms_torque_nm, abs=1e-12
        )


def test_positive_added_inertia_adds_torque_in_acceleration_direction() -> None:
    trajectory = generate_trajectory()
    result = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    zero_inertia = TransmissionInertiaModel(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    zero = DriveTransmission(
        ratio=INDUSTRIAL_REFERENCE_TRANSMISSION.ratio,
        efficiency=INDUSTRIAL_REFERENCE_TRANSMISSION.efficiency,
        small_pulley_pitch_radius_m=(
            INDUSTRIAL_REFERENCE_TRANSMISSION.small_pulley_pitch_radius_m
        ),
        inertia=zero_inertia,
    )
    baseline = assess_refined_drive(
        trajectory, result, LEADSHINE_ISV2_RS6040V48G, zero
    )
    refined = assess_refined_drive(
        trajectory,
        result,
        LEADSHINE_ISV2_RS6040V48G,
        INDUSTRIAL_REFERENCE_TRANSMISSION,
    )
    sample_index = 200
    acceleration = trajectory.samples[sample_index].joint_accelerations.theta_1_rad_s2
    increment = (
        refined.motor_torques_nm[sample_index][0]
        - baseline.motor_torques_nm[sample_index][0]
    )

    assert acceleration != 0.0
    assert math.copysign(1.0, increment) == math.copysign(1.0, acceleration)


def test_effective_joint_inertias_are_positive_and_symmetric_at_center() -> None:
    differential = differential_kinematics(
        SELECTED_GEOMETRY,
        CartesianPosition(0.0, 0.0, -0.347),
        AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
    )

    inertias = joint_effective_inertias_kg_m2(differential, CONSERVATIVE_MASS_CASE)

    assert min(inertias) > 0.0
    assert inertias[0] == pytest.approx(inertias[1], abs=1e-12)
    assert inertias[0] == pytest.approx(inertias[2], abs=1e-12)
