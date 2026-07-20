import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from delta_model import GeometryValidationError
from delta_model.williams import (
    ANGLE_ABS_TOLERANCE_RAD,
    POSITION_ABS_TOLERANCE_M,
    WILLIAMS_DIMENSIONS,
    WILLIAMS_FK_CASES,
    WILLIAMS_GEOMETRY,
    WILLIAMS_IK_CASES,
    WilliamsDimensions,
    adapt_williams_geometry,
)


def test_williams_adapter_matches_precomputed_reference_radii() -> None:
    assert WILLIAMS_GEOMETRY.base_joint_radius_m == pytest.approx(
        0.1636788013152589,
        abs=1e-15,
    )
    assert WILLIAMS_GEOMETRY.platform_joint_radius_m == pytest.approx(
        0.04387862045841156,
        abs=1e-15,
    )
    assert WILLIAMS_GEOMETRY.upper_arm_length_m == 0.524
    assert WILLIAMS_GEOMETRY.lower_arm_length_m == 1.244
    assert WILLIAMS_GEOMETRY.min_joint_angle_rad == -math.pi
    assert WILLIAMS_GEOMETRY.max_joint_angle_rad == math.pi


@given(
    base_side=st.floats(min_value=1e-6, max_value=10.0, allow_nan=False),
    platform_side=st.floats(min_value=1e-6, max_value=10.0, allow_nan=False),
)
def test_adapter_radii_reconstruct_source_triangle_sides(
    base_side: float,
    platform_side: float,
) -> None:
    geometry = adapt_williams_geometry(
        WilliamsDimensions(
            base_triangle_side_m=base_side,
            platform_triangle_side_m=platform_side,
            upper_arm_length_m=0.5,
            lower_arm_length_m=1.0,
        ),
        min_joint_angle_rad=-math.pi,
        max_joint_angle_rad=math.pi,
    )

    assert geometry.base_joint_radius_m * 2.0 * math.sqrt(3.0) == pytest.approx(base_side)
    assert geometry.platform_joint_radius_m * math.sqrt(3.0) == pytest.approx(platform_side)


@pytest.mark.parametrize("invalid_side", [0.0, -0.1, math.nan, math.inf])
def test_adapter_rejects_invalid_source_side(invalid_side: float) -> None:
    invalid_dimensions = WilliamsDimensions(
        base_triangle_side_m=invalid_side,
        platform_triangle_side_m=WILLIAMS_DIMENSIONS.platform_triangle_side_m,
        upper_arm_length_m=WILLIAMS_DIMENSIONS.upper_arm_length_m,
        lower_arm_length_m=WILLIAMS_DIMENSIONS.lower_arm_length_m,
    )

    with pytest.raises(GeometryValidationError, match="base_joint_radius_m"):
        adapt_williams_geometry(
            invalid_dimensions,
            min_joint_angle_rad=-math.pi,
            max_joint_angle_rad=math.pi,
        )


@pytest.mark.parametrize(
    ("case", "position_m", "angles_deg"),
    [
        (WILLIAMS_IK_CASES[0], (0.0, 0.0, -0.900), (-20.5, -20.5, -20.5)),
        (WILLIAMS_IK_CASES[1], (0.300, 0.500, -1.100), (47.5, -11.6, 21.4)),
    ],
    ids=("ik-centered", "ik-offset"),
)
def test_published_inverse_case_is_transcribed_in_si(
    case: object,
    position_m: tuple[float, float, float],
    angles_deg: tuple[float, float, float],
) -> None:
    assert case in WILLIAMS_IK_CASES
    typed_case = next(reference for reference in WILLIAMS_IK_CASES if reference is case)

    assert (
        typed_case.position.x_m,
        typed_case.position.y_m,
        typed_case.position.z_m,
    ) == position_m
    assert (
        typed_case.expected_angles.theta_1_rad,
        typed_case.expected_angles.theta_2_rad,
        typed_case.expected_angles.theta_3_rad,
    ) == pytest.approx(tuple(math.radians(angle) for angle in angles_deg))
    assert typed_case.angle_abs_tolerance_rad == ANGLE_ABS_TOLERANCE_RAD


@pytest.mark.parametrize(
    ("case", "angles_deg", "position_m"),
    [
        (WILLIAMS_FK_CASES[0], (0.0, 0.0, 0.0), (0.0, 0.0, -1.065)),
        (WILLIAMS_FK_CASES[1], (10.0, 20.0, 30.0), (0.108, -0.180, -1.244)),
    ],
    ids=("fk-zero-angles", "fk-distinct-angles"),
)
def test_published_forward_case_is_transcribed_in_si(
    case: object,
    angles_deg: tuple[float, float, float],
    position_m: tuple[float, float, float],
) -> None:
    assert case in WILLIAMS_FK_CASES
    typed_case = next(reference for reference in WILLIAMS_FK_CASES if reference is case)

    assert (
        typed_case.angles.theta_1_rad,
        typed_case.angles.theta_2_rad,
        typed_case.angles.theta_3_rad,
    ) == pytest.approx(tuple(math.radians(angle) for angle in angles_deg))
    assert (
        typed_case.expected_position.x_m,
        typed_case.expected_position.y_m,
        typed_case.expected_position.z_m,
    ) == position_m
    assert typed_case.position_abs_tolerance_m == POSITION_ABS_TOLERANCE_M
