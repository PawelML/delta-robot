import math
from dataclasses import replace

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.differential_kinematics import (
    CartesianAcceleration,
    CartesianVelocity,
    InvalidVelocityError,
    JointRates,
    cartesian_velocity_for_joint_rates,
    differential_kinematics,
    joint_accelerations_for_cartesian_motion,
    joint_rates_for_cartesian_velocity,
)
from delta_model.williams import WILLIAMS_GEOMETRY

ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW


def _rate_tuple(rates: JointRates) -> tuple[float, float, float]:
    return (rates.theta_1_rad_s, rates.theta_2_rad_s, rates.theta_3_rad_s)


def test_williams_center_has_symmetric_matrices_and_metrics() -> None:
    result = differential_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(0.0, 0.0, -0.9),
        ASSEMBLY_MODE,
    )

    diagonal = np.diag(np.asarray(result.joint_constraint_matrix_m))
    assert diagonal[0] == pytest.approx(diagonal[1], abs=1e-12)
    assert diagonal[0] == pytest.approx(diagonal[2], abs=1e-12)
    assert result.metrics.serial_margin_by_arm[0] == pytest.approx(
        result.metrics.serial_margin_by_arm[1], abs=1e-12
    )
    assert result.metrics.serial_margin_by_arm[0] == pytest.approx(
        result.metrics.serial_margin_by_arm[2], abs=1e-12
    )
    assert 0.0 < result.metrics.singularity_margin <= 1.0


def test_velocity_maps_are_mutual_inverses_and_satisfy_constraint() -> None:
    result = differential_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(0.12, -0.08, -1.0),
        ASSEMBLY_MODE,
    )
    requested = CartesianVelocity(0.17, -0.09, 0.04)

    rates = joint_rates_for_cartesian_velocity(result, requested)
    recovered = cartesian_velocity_for_joint_rates(result, rates)

    assert recovered.x_m_s == pytest.approx(requested.x_m_s, abs=1e-12)
    assert recovered.y_m_s == pytest.approx(requested.y_m_s, abs=1e-12)
    assert recovered.z_m_s == pytest.approx(requested.z_m_s, abs=1e-12)
    residual = np.asarray(result.cartesian_constraint_matrix) @ np.asarray(
        (requested.x_m_s, requested.y_m_s, requested.z_m_s)
    ) - np.asarray(result.joint_constraint_matrix_m) @ np.asarray(_rate_tuple(rates))
    assert float(np.max(np.abs(residual))) < 1e-12


def test_analytic_joint_rates_match_central_difference_of_independent_ik_calls() -> None:
    position = CartesianPosition(0.12, -0.08, -1.0)
    velocity = CartesianVelocity(0.17, -0.09, 0.04)
    result = differential_kinematics(WILLIAMS_GEOMETRY, position, ASSEMBLY_MODE)
    analytical = _rate_tuple(joint_rates_for_cartesian_velocity(result, velocity))
    step_s = 1e-6
    before = differential_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(
            position.x_m - step_s * velocity.x_m_s,
            position.y_m - step_s * velocity.y_m_s,
            position.z_m - step_s * velocity.z_m_s,
        ),
        ASSEMBLY_MODE,
    ).inverse_result.angles
    after = differential_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(
            position.x_m + step_s * velocity.x_m_s,
            position.y_m + step_s * velocity.y_m_s,
            position.z_m + step_s * velocity.z_m_s,
        ),
        ASSEMBLY_MODE,
    ).inverse_result.angles
    finite_difference = (
        (after.theta_1_rad - before.theta_1_rad) / (2.0 * step_s),
        (after.theta_2_rad - before.theta_2_rad) / (2.0 * step_s),
        (after.theta_3_rad - before.theta_3_rad) / (2.0 * step_s),
    )

    assert finite_difference == pytest.approx(analytical, abs=1e-9)


def test_analytic_joint_acceleration_matches_central_difference_of_joint_rates() -> None:
    position = CartesianPosition(0.12, -0.08, -1.0)
    velocity = CartesianVelocity(0.17, -0.09, 0.04)
    acceleration = CartesianAcceleration(0.8, -0.3, 0.2)
    result = differential_kinematics(WILLIAMS_GEOMETRY, position, ASSEMBLY_MODE)
    rates = joint_rates_for_cartesian_velocity(result, velocity)
    analytical = joint_accelerations_for_cartesian_motion(
        result,
        velocity,
        acceleration,
        rates,
    )
    step_s = 1e-6

    def rates_at(offset_s: float) -> tuple[float, float, float]:
        offset_position = CartesianPosition(
            position.x_m
            + velocity.x_m_s * offset_s
            + 0.5 * acceleration.x_m_s2 * offset_s * offset_s,
            position.y_m
            + velocity.y_m_s * offset_s
            + 0.5 * acceleration.y_m_s2 * offset_s * offset_s,
            position.z_m
            + velocity.z_m_s * offset_s
            + 0.5 * acceleration.z_m_s2 * offset_s * offset_s,
        )
        offset_velocity = CartesianVelocity(
            velocity.x_m_s + acceleration.x_m_s2 * offset_s,
            velocity.y_m_s + acceleration.y_m_s2 * offset_s,
            velocity.z_m_s + acceleration.z_m_s2 * offset_s,
        )
        offset_result = differential_kinematics(
            WILLIAMS_GEOMETRY,
            offset_position,
            ASSEMBLY_MODE,
        )
        return _rate_tuple(joint_rates_for_cartesian_velocity(offset_result, offset_velocity))

    before = rates_at(-step_s)
    after = rates_at(step_s)
    finite_difference = tuple(
        (after[index] - before[index]) / (2.0 * step_s) for index in range(3)
    )

    assert finite_difference == pytest.approx(
        (
            analytical.theta_1_rad_s2,
            analytical.theta_2_rad_s2,
            analytical.theta_3_rad_s2,
        ),
        abs=1e-7,
    )


@given(scale=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=50, deadline=None)
def test_uniform_length_scaling_preserves_singularity_metrics(scale: float) -> None:
    position = CartesianPosition(0.12, -0.08, -1.0)
    base = differential_kinematics(WILLIAMS_GEOMETRY, position, ASSEMBLY_MODE).metrics
    scaled_geometry = replace(
        WILLIAMS_GEOMETRY,
        base_joint_radius_m=WILLIAMS_GEOMETRY.base_joint_radius_m * scale,
        platform_joint_radius_m=WILLIAMS_GEOMETRY.platform_joint_radius_m * scale,
        upper_arm_length_m=WILLIAMS_GEOMETRY.upper_arm_length_m * scale,
        lower_arm_length_m=WILLIAMS_GEOMETRY.lower_arm_length_m * scale,
    )
    scaled = differential_kinematics(
        scaled_geometry,
        CartesianPosition(position.x_m * scale, position.y_m * scale, position.z_m * scale),
        ASSEMBLY_MODE,
    ).metrics

    assert scaled.parallel_margin == pytest.approx(base.parallel_margin, abs=1e-12)
    assert scaled.serial_margin == pytest.approx(base.serial_margin, abs=1e-12)
    assert scaled.singularity_margin == pytest.approx(base.singularity_margin, abs=1e-12)


@pytest.mark.parametrize(
    "velocity",
    [CartesianVelocity(math.nan, 0.0, 0.0), CartesianVelocity(0.0, math.inf, 0.0)],
)
def test_non_finite_cartesian_velocity_is_rejected(velocity: CartesianVelocity) -> None:
    result = differential_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(0.0, 0.0, -0.9),
        ASSEMBLY_MODE,
    )
    with pytest.raises(InvalidVelocityError, match="must be finite"):
        joint_rates_for_cartesian_velocity(result, velocity)
