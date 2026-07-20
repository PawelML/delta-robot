import math
from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from delta_model import (
    AssemblyConstraintError,
    AssemblyMode,
    CartesianPoint,
    CartesianPosition,
    InvalidPositionError,
    JointLimitError,
    UnreachablePositionError,
    inverse_kinematics,
)
from delta_model.inverse_kinematics import InverseKinematicsResult
from delta_model.williams import (
    WILLIAMS_GEOMETRY,
    WILLIAMS_IK_CASES,
    InverseKinematicsReferenceCase,
)

ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW
LINK_CLOSURE_ABS_TOLERANCE_M = 1e-12


def _distance_m(point_a: CartesianPoint, point_b: CartesianPoint) -> float:
    coordinates_a = (point_a.x_m, point_a.y_m, point_a.z_m)
    coordinates_b = (point_b.x_m, point_b.y_m, point_b.z_m)
    return math.dist(coordinates_a, coordinates_b)


@pytest.mark.parametrize("case", WILLIAMS_IK_CASES, ids=lambda case: case.case_id)
def test_inverse_kinematics_matches_williams_published_cases(
    case: InverseKinematicsReferenceCase,
) -> None:
    result = inverse_kinematics(WILLIAMS_GEOMETRY, case.position, ASSEMBLY_MODE)

    actual = (
        result.angles.theta_1_rad,
        result.angles.theta_2_rad,
        result.angles.theta_3_rad,
    )
    expected = (
        case.expected_angles.theta_1_rad,
        case.expected_angles.theta_2_rad,
        case.expected_angles.theta_3_rad,
    )
    assert actual == pytest.approx(expected, abs=case.angle_abs_tolerance_rad)


def test_centered_position_produces_three_equal_angles() -> None:
    result = inverse_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.9),
        ASSEMBLY_MODE,
    )

    assert result.angles.theta_1_rad == pytest.approx(result.angles.theta_2_rad, abs=1e-15)
    assert result.angles.theta_2_rad == pytest.approx(result.angles.theta_3_rad, abs=1e-15)


def test_rotating_position_by_120_degrees_cyclically_permutes_angles() -> None:
    position = CartesianPosition(x_m=0.3, y_m=0.5, z_m=-1.1)
    original = inverse_kinematics(WILLIAMS_GEOMETRY, position, ASSEMBLY_MODE)
    rotation = 2.0 * math.pi / 3.0
    rotated_position = CartesianPosition(
        x_m=position.x_m * math.cos(rotation) - position.y_m * math.sin(rotation),
        y_m=position.x_m * math.sin(rotation) + position.y_m * math.cos(rotation),
        z_m=position.z_m,
    )

    rotated = inverse_kinematics(WILLIAMS_GEOMETRY, rotated_position, ASSEMBLY_MODE)

    assert rotated.angles.theta_1_rad == pytest.approx(original.angles.theta_3_rad, abs=1e-12)
    assert rotated.angles.theta_2_rad == pytest.approx(original.angles.theta_1_rad, abs=1e-12)
    assert rotated.angles.theta_3_rad == pytest.approx(original.angles.theta_2_rad, abs=1e-12)


@given(
    x_m=st.floats(min_value=-0.1, max_value=0.1, allow_nan=False),
    y_m=st.floats(min_value=-0.1, max_value=0.1, allow_nan=False),
    z_m=st.floats(min_value=-1.15, max_value=-0.85, allow_nan=False),
)
def test_returned_points_close_upper_and_lower_links(
    x_m: float,
    y_m: float,
    z_m: float,
) -> None:
    result = inverse_kinematics(
        WILLIAMS_GEOMETRY,
        CartesianPosition(x_m=x_m, y_m=y_m, z_m=z_m),
        ASSEMBLY_MODE,
    )

    _assert_link_closure(result)


def _assert_link_closure(result: InverseKinematicsResult) -> None:
    for arm in result.arm_solutions:
        assert _distance_m(arm.shoulder_point, arm.knee_point) == pytest.approx(
            WILLIAMS_GEOMETRY.upper_arm_length_m,
            abs=LINK_CLOSURE_ABS_TOLERANCE_M,
        )
        assert _distance_m(arm.knee_point, arm.platform_attachment_point) == pytest.approx(
            WILLIAMS_GEOMETRY.lower_arm_length_m,
            abs=LINK_CLOSURE_ABS_TOLERANCE_M,
        )


def test_geometrically_unreachable_position_is_explicit() -> None:
    with pytest.raises(UnreachablePositionError, match="arm 1"):
        inverse_kinematics(
            WILLIAMS_GEOMETRY,
            CartesianPosition(x_m=10.0, y_m=0.0, z_m=-0.9),
            ASSEMBLY_MODE,
        )


def test_joint_limit_failure_is_distinct_from_unreachable_position() -> None:
    positive_angles_only = replace(
        WILLIAMS_GEOMETRY,
        min_joint_angle_rad=0.0,
        max_joint_angle_rad=math.pi,
    )

    with pytest.raises(JointLimitError, match="arm 1"):
        inverse_kinematics(
            positive_angles_only,
            CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.9),
            ASSEMBLY_MODE,
        )


def test_platform_above_base_is_rejected_for_supported_assembly() -> None:
    with pytest.raises(AssemblyConstraintError, match="below zero"):
        inverse_kinematics(
            WILLIAMS_GEOMETRY,
            CartesianPosition(x_m=0.0, y_m=0.0, z_m=0.9),
            ASSEMBLY_MODE,
        )


@pytest.mark.parametrize("invalid_component", [math.nan, math.inf, -math.inf])
def test_non_finite_position_is_rejected(invalid_component: float) -> None:
    with pytest.raises(InvalidPositionError, match="must be finite"):
        inverse_kinematics(
            WILLIAMS_GEOMETRY,
            CartesianPosition(x_m=invalid_component, y_m=0.0, z_m=-0.9),
            ASSEMBLY_MODE,
        )
