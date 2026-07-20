"""Adapter and published reference fixtures from Williams (2016)."""

import math
from dataclasses import dataclass

from delta_model.conventions import CartesianPosition, JointAngles
from delta_model.geometry import DeltaGeometry

SOURCE_URL = "https://sites.ohio.edu/williams/html/PDF/DeltaKin.pdf"

ANGLE_REPORTING_RESOLUTION_DEG = 0.1
POSITION_REPORTING_RESOLUTION_M = 0.001
FLOAT_BOUNDARY_SLACK = 1e-12
ANGLE_ABS_TOLERANCE_RAD = (
    math.radians(ANGLE_REPORTING_RESOLUTION_DEG) / 2.0 + FLOAT_BOUNDARY_SLACK
)
POSITION_ABS_TOLERANCE_M = POSITION_REPORTING_RESOLUTION_M / 2.0 + FLOAT_BOUNDARY_SLACK


@dataclass(frozen=True, slots=True)
class WilliamsDimensions:
    """Triangle-side notation used by the Williams reference, in metres."""

    base_triangle_side_m: float
    platform_triangle_side_m: float
    upper_arm_length_m: float
    lower_arm_length_m: float


def adapt_williams_geometry(
    dimensions: WilliamsDimensions,
    *,
    min_joint_angle_rad: float,
    max_joint_angle_rad: float,
) -> DeltaGeometry:
    """Convert Williams triangle sides to the P0 center-to-joint radii."""

    return DeltaGeometry(
        base_joint_radius_m=dimensions.base_triangle_side_m / (2.0 * math.sqrt(3.0)),
        platform_joint_radius_m=dimensions.platform_triangle_side_m / math.sqrt(3.0),
        upper_arm_length_m=dimensions.upper_arm_length_m,
        lower_arm_length_m=dimensions.lower_arm_length_m,
        min_joint_angle_rad=min_joint_angle_rad,
        max_joint_angle_rad=max_joint_angle_rad,
    )


WILLIAMS_DIMENSIONS = WilliamsDimensions(
    base_triangle_side_m=0.567,
    platform_triangle_side_m=0.076,
    upper_arm_length_m=0.524,
    lower_arm_length_m=1.244,
)

WILLIAMS_GEOMETRY = adapt_williams_geometry(
    WILLIAMS_DIMENSIONS,
    min_joint_angle_rad=-math.pi,
    max_joint_angle_rad=math.pi,
)


@dataclass(frozen=True, slots=True)
class InverseKinematicsReferenceCase:
    """Published platform position and rounded expected shoulder angles."""

    case_id: str
    position: CartesianPosition
    expected_angles: JointAngles
    angle_abs_tolerance_rad: float = ANGLE_ABS_TOLERANCE_RAD


@dataclass(frozen=True, slots=True)
class ForwardKinematicsReferenceCase:
    """Published shoulder angles and rounded expected platform position."""

    case_id: str
    angles: JointAngles
    expected_position: CartesianPosition
    position_abs_tolerance_m: float = POSITION_ABS_TOLERANCE_M


WILLIAMS_IK_CASES = (
    InverseKinematicsReferenceCase(
        case_id="ik-centered",
        position=CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.900),
        expected_angles=JointAngles(
            theta_1_rad=math.radians(-20.5),
            theta_2_rad=math.radians(-20.5),
            theta_3_rad=math.radians(-20.5),
        ),
    ),
    InverseKinematicsReferenceCase(
        case_id="ik-offset",
        position=CartesianPosition(x_m=0.300, y_m=0.500, z_m=-1.100),
        expected_angles=JointAngles(
            theta_1_rad=math.radians(47.5),
            theta_2_rad=math.radians(-11.6),
            theta_3_rad=math.radians(21.4),
        ),
    ),
)

WILLIAMS_FK_CASES = (
    ForwardKinematicsReferenceCase(
        case_id="fk-zero-angles",
        angles=JointAngles(theta_1_rad=0.0, theta_2_rad=0.0, theta_3_rad=0.0),
        expected_position=CartesianPosition(x_m=0.0, y_m=0.0, z_m=-1.065),
    ),
    ForwardKinematicsReferenceCase(
        case_id="fk-distinct-angles",
        angles=JointAngles(
            theta_1_rad=math.radians(10.0),
            theta_2_rad=math.radians(20.0),
            theta_3_rad=math.radians(30.0),
        ),
        expected_position=CartesianPosition(x_m=0.108, y_m=-0.180, z_m=-1.244),
    ),
)
