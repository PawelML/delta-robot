import math
import random
from dataclasses import replace

import pytest

from delta_model import (
    AssemblyConstraintError,
    AssemblyMode,
    CartesianPoint,
    CartesianPosition,
    DegenerateSphereGeometryError,
    InvalidAnglesError,
    JointAngles,
    JointLimitError,
    UnreachableAnglesError,
    forward_kinematics,
    intersect_three_equal_spheres,
    inverse_kinematics,
)
from delta_model.williams import (
    WILLIAMS_FK_CASES,
    WILLIAMS_GEOMETRY,
    ForwardKinematicsReferenceCase,
)

ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW
LINK_CLOSURE_ABS_TOLERANCE_M = 1e-12
ROUND_TRIP_GATE_M = 1e-5
ROUND_TRIP_SAMPLE_COUNT = 10_000
ROUND_TRIP_SEED = 20260720


def _coordinates(point: CartesianPoint | CartesianPosition) -> tuple[float, float, float]:
    return (point.x_m, point.y_m, point.z_m)


@pytest.mark.parametrize("case", WILLIAMS_FK_CASES, ids=lambda case: case.case_id)
def test_forward_kinematics_matches_williams_published_cases(
    case: ForwardKinematicsReferenceCase,
) -> None:
    result = forward_kinematics(WILLIAMS_GEOMETRY, case.angles, ASSEMBLY_MODE)

    assert _coordinates(result.position) == pytest.approx(
        _coordinates(case.expected_position),
        abs=case.position_abs_tolerance_m,
    )


def test_equal_knee_height_case_returns_centered_platform_below_base() -> None:
    result = forward_kinematics(
        WILLIAMS_GEOMETRY,
        JointAngles(theta_1_rad=0.0, theta_2_rad=0.0, theta_3_rad=0.0),
        ASSEMBLY_MODE,
    )

    assert result.position.x_m == pytest.approx(0.0, abs=1e-15)
    assert result.position.y_m == pytest.approx(0.0, abs=1e-15)
    assert result.position.z_m < 0.0
    assert len(result.position_candidates) == 2
    assert sum(candidate.z_m < 0.0 for candidate in result.position_candidates) == 1


def test_three_sphere_intersection_matches_analytic_symmetric_case() -> None:
    candidates = intersect_three_equal_spheres(
        CartesianPoint(x_m=0.0, y_m=0.0, z_m=0.0),
        CartesianPoint(x_m=2.0, y_m=0.0, z_m=0.0),
        CartesianPoint(x_m=1.0, y_m=math.sqrt(3.0), z_m=0.0),
        radius_m=2.0,
    )

    expected_xy = (1.0, math.sqrt(3.0) / 3.0)
    expected_abs_z = math.sqrt(8.0 / 3.0)
    for candidate in candidates:
        assert (candidate.x_m, candidate.y_m) == pytest.approx(expected_xy, abs=1e-15)
        assert abs(candidate.z_m) == pytest.approx(expected_abs_z, abs=1e-15)


@pytest.mark.parametrize("case", WILLIAMS_FK_CASES, ids=lambda case: case.case_id)
def test_forward_diagnostic_points_close_both_link_lengths(
    case: ForwardKinematicsReferenceCase,
) -> None:
    result = forward_kinematics(WILLIAMS_GEOMETRY, case.angles, ASSEMBLY_MODE)

    for arm in result.arm_poses:
        assert math.dist(
            _coordinates(arm.shoulder_point),
            _coordinates(arm.knee_point),
        ) == pytest.approx(
            WILLIAMS_GEOMETRY.upper_arm_length_m,
            abs=LINK_CLOSURE_ABS_TOLERANCE_M,
        )
        assert math.dist(
            _coordinates(arm.knee_point),
            _coordinates(arm.platform_attachment_point),
        ) == pytest.approx(
            WILLIAMS_GEOMETRY.lower_arm_length_m,
            abs=LINK_CLOSURE_ABS_TOLERANCE_M,
        )


def test_three_spheres_without_common_point_are_rejected() -> None:
    with pytest.raises(UnreachableAnglesError, match="no common point"):
        intersect_three_equal_spheres(
            CartesianPoint(x_m=0.0, y_m=0.0, z_m=0.0),
            CartesianPoint(x_m=3.0, y_m=0.0, z_m=0.0),
            CartesianPoint(x_m=0.0, y_m=3.0, z_m=0.0),
            radius_m=1.0,
        )


def test_collinear_sphere_centers_are_reported_as_degenerate() -> None:
    with pytest.raises(DegenerateSphereGeometryError, match="collinear"):
        intersect_three_equal_spheres(
            CartesianPoint(x_m=0.0, y_m=0.0, z_m=0.0),
            CartesianPoint(x_m=1.0, y_m=0.0, z_m=0.0),
            CartesianPoint(x_m=2.0, y_m=0.0, z_m=0.0),
            radius_m=2.0,
        )


@pytest.mark.parametrize("invalid_angle", [math.nan, math.inf, -math.inf])
def test_non_finite_angle_is_rejected(invalid_angle: float) -> None:
    with pytest.raises(InvalidAnglesError, match="must be finite"):
        forward_kinematics(
            WILLIAMS_GEOMETRY,
            JointAngles(
                theta_1_rad=invalid_angle,
                theta_2_rad=0.0,
                theta_3_rad=0.0,
            ),
            ASSEMBLY_MODE,
        )


def test_forward_kinematics_enforces_joint_limits() -> None:
    narrow_limits = replace(
        WILLIAMS_GEOMETRY,
        min_joint_angle_rad=math.radians(-5.0),
        max_joint_angle_rad=math.radians(5.0),
    )

    with pytest.raises(JointLimitError, match="arm 1"):
        forward_kinematics(
            narrow_limits,
            JointAngles(theta_1_rad=0.2, theta_2_rad=0.0, theta_3_rad=0.0),
            ASSEMBLY_MODE,
        )


def test_forward_kinematics_rejects_knee_in_angles() -> None:
    with pytest.raises(AssemblyConstraintError, match="arm 1"):
        forward_kinematics(
            WILLIAMS_GEOMETRY,
            JointAngles(theta_1_rad=2.0, theta_2_rad=0.0, theta_3_rad=0.0),
            ASSEMBLY_MODE,
        )


def test_ik_to_fk_round_trip_gate_for_10000_positions() -> None:
    random_generator = random.Random(ROUND_TRIP_SEED)
    errors_m: list[float] = []

    for _ in range(ROUND_TRIP_SAMPLE_COUNT):
        requested = CartesianPosition(
            x_m=random_generator.uniform(-0.1, 0.1),
            y_m=random_generator.uniform(-0.1, 0.1),
            z_m=random_generator.uniform(-1.15, -0.85),
        )
        inverse_result = inverse_kinematics(WILLIAMS_GEOMETRY, requested, ASSEMBLY_MODE)
        forward_result = forward_kinematics(
            WILLIAMS_GEOMETRY,
            inverse_result.angles,
            ASSEMBLY_MODE,
        )
        errors_m.append(math.dist(_coordinates(requested), _coordinates(forward_result.position)))

    sorted_errors_m = sorted(errors_m)
    maximum_error_m = sorted_errors_m[-1]
    percentile_99_error_m = sorted_errors_m[math.ceil(0.99 * len(sorted_errors_m)) - 1]
    summary = f"max={maximum_error_m:.3e} m, p99={percentile_99_error_m:.3e} m"

    assert maximum_error_m < ROUND_TRIP_GATE_M, summary
    assert percentile_99_error_m < ROUND_TRIP_GATE_M, summary
