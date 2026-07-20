"""Inverse position kinematics for the supported rotary-delta assembly branch."""

import math
import sys
from dataclasses import dataclass

from delta_model.arm_geometry import (
    arm_radial_vector,
    knee_point,
    platform_attachment_point,
    shoulder_point,
)
from delta_model.conventions import (
    AssemblyMode,
    CartesianPoint,
    CartesianPosition,
    JointAngles,
)
from delta_model.errors import (
    AssemblyConstraintError,
    JointLimitError,
    KinematicsError,
    UnsupportedAssemblyModeError,
)
from delta_model.geometry import DeltaGeometry

DISCRIMINANT_RELATIVE_TOLERANCE = 64.0 * sys.float_info.epsilon

class InverseKinematicsError(KinematicsError):
    """Base class for inverse-specific solver failures."""


class InvalidPositionError(InverseKinematicsError):
    """Raised when a requested platform position is not finite."""


class UnreachablePositionError(InverseKinematicsError):
    """Raised when an arm cannot close at the requested position."""


class DegeneratePositionError(InverseKinematicsError):
    """Raised at a collapsed or numerically indistinguishable IK boundary."""


class AmbiguousAssemblyError(InverseKinematicsError):
    """Raised when the assembly rule does not select exactly one root."""


@dataclass(frozen=True, slots=True)
class ArmInverseSolution:
    """One arm angle and the three points that demonstrate link closure."""

    arm_index: int
    angle_rad: float
    shoulder_point: CartesianPoint
    knee_point: CartesianPoint
    platform_attachment_point: CartesianPoint


@dataclass(frozen=True, slots=True)
class InverseKinematicsResult:
    """Complete three-arm IK result for one platform-center position."""

    angles: JointAngles
    arm_solutions: tuple[ArmInverseSolution, ArmInverseSolution, ArmInverseSolution]


def _validate_position(position: CartesianPosition) -> None:
    if not all(math.isfinite(value) for value in (position.x_m, position.y_m, position.z_m)):
        raise InvalidPositionError("platform position components must be finite")


def _normalize_angle(angle_rad: float) -> float:
    return math.atan2(math.sin(angle_rad), math.cos(angle_rad))


def _validate_assembly(position: CartesianPosition, assembly_mode: AssemblyMode) -> None:
    if assembly_mode is not AssemblyMode.KNEE_OUT_PLATFORM_BELOW:
        raise UnsupportedAssemblyModeError(f"unsupported assembly mode: {assembly_mode!r}")
    if position.z_m >= 0.0:
        raise AssemblyConstraintError(
            "knee_out_platform_below requires platform position z_m to be below zero"
        )


def solve_arm_inverse(
    geometry: DeltaGeometry,
    position: CartesianPosition,
    arm_index: int,
    assembly_mode: AssemblyMode,
) -> ArmInverseSolution:
    """Solve one motor-plane circle/sphere intersection for the requested branch."""

    _validate_position(position)
    _validate_assembly(position, assembly_mode)
    radial_x, radial_y = arm_radial_vector(arm_index)
    radial_distance = (
        position.x_m * radial_x
        + position.y_m * radial_y
        + geometry.platform_joint_radius_m
        - geometry.base_joint_radius_m
    )
    tangential_distance = -position.x_m * radial_y + position.y_m * radial_x

    upper_length = geometry.upper_arm_length_m
    lower_length = geometry.lower_arm_length_m
    coefficient_e = -2.0 * upper_length * radial_distance
    coefficient_f = 2.0 * upper_length * position.z_m
    coefficient_g = (
        radial_distance * radial_distance
        + tangential_distance * tangential_distance
        + position.z_m * position.z_m
        + upper_length * upper_length
        - lower_length * lower_length
    )

    phase_radius = math.hypot(coefficient_e, coefficient_f)
    coefficient_scale = max(abs(coefficient_e), abs(coefficient_f), abs(coefficient_g))
    if phase_radius <= DISCRIMINANT_RELATIVE_TOLERANCE * coefficient_scale:
        raise DegeneratePositionError(f"arm {arm_index} has a collapsed phase equation")

    discriminant = phase_radius * phase_radius - coefficient_g * coefficient_g
    discriminant_scale = max(phase_radius * phase_radius, coefficient_g * coefficient_g)
    discriminant_tolerance = DISCRIMINANT_RELATIVE_TOLERANCE * discriminant_scale
    if discriminant < -discriminant_tolerance:
        raise UnreachablePositionError(f"arm {arm_index} cannot reach the platform attachment")
    if abs(discriminant) <= discriminant_tolerance:
        raise DegeneratePositionError(f"arm {arm_index} is at a tangent reach boundary")

    cosine_argument = -coefficient_g / phase_radius
    if not -1.0 < cosine_argument < 1.0:
        raise DegeneratePositionError(f"arm {arm_index} root is at a numerical boundary")

    phase_angle = math.atan2(coefficient_f, coefficient_e)
    root_offset = math.acos(cosine_argument)
    roots = (
        _normalize_angle(phase_angle + root_offset),
        _normalize_angle(phase_angle - root_offset),
    )
    outward_tolerance_m = DISCRIMINANT_RELATIVE_TOLERANCE * upper_length
    outward_roots = tuple(
        root for root in roots if upper_length * math.cos(root) > outward_tolerance_m
    )
    if len(outward_roots) != 1:
        raise AmbiguousAssemblyError(
            f"arm {arm_index} has {len(outward_roots)} knee-out roots; expected exactly one"
        )

    angle_rad = outward_roots[0]
    if not geometry.min_joint_angle_rad <= angle_rad <= geometry.max_joint_angle_rad:
        raise JointLimitError(
            f"arm {arm_index} angle {angle_rad} rad is outside "
            f"[{geometry.min_joint_angle_rad}, {geometry.max_joint_angle_rad}] rad"
        )

    shoulder = shoulder_point(geometry, arm_index)
    knee = knee_point(geometry, arm_index, angle_rad)
    attachment = platform_attachment_point(geometry, position, arm_index)
    return ArmInverseSolution(
        arm_index=arm_index,
        angle_rad=angle_rad,
        shoulder_point=shoulder,
        knee_point=knee,
        platform_attachment_point=attachment,
    )


def inverse_kinematics(
    geometry: DeltaGeometry,
    position: CartesianPosition,
    assembly_mode: AssemblyMode,
) -> InverseKinematicsResult:
    """Solve all three independent arms for a platform-center position."""

    _validate_position(position)
    arms = (
        solve_arm_inverse(geometry, position, 1, assembly_mode),
        solve_arm_inverse(geometry, position, 2, assembly_mode),
        solve_arm_inverse(geometry, position, 3, assembly_mode),
    )
    return InverseKinematicsResult(
        angles=JointAngles(
            theta_1_rad=arms[0].angle_rad,
            theta_2_rad=arms[1].angle_rad,
            theta_3_rad=arms[2].angle_rad,
        ),
        arm_solutions=arms,
    )
