"""Forward position kinematics via intersection of three lower-link spheres."""

import math
import sys
from dataclasses import dataclass

from delta_model.arm_geometry import (
    knee_point,
    platform_attachment_point,
    shoulder_point,
    virtual_sphere_center,
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

GEOMETRIC_RELATIVE_TOLERANCE = 64.0 * sys.float_info.epsilon

Vector3 = tuple[float, float, float]


class ForwardKinematicsError(KinematicsError):
    """Base class for forward-specific solver failures."""


class InvalidAnglesError(ForwardKinematicsError):
    """Raised when at least one requested shoulder angle is not finite."""


class UnreachableAnglesError(ForwardKinematicsError):
    """Raised when the three lower-link spheres have no common point."""


class DegenerateSphereGeometryError(ForwardKinematicsError):
    """Raised when sphere intersection collapses at a geometric boundary."""


class AmbiguousForwardSolutionError(ForwardKinematicsError):
    """Raised when the assembly rule does not select exactly one candidate."""


@dataclass(frozen=True, slots=True)
class ArmForwardPose:
    """Known and reconstructed points for one arm in an FK result."""

    arm_index: int
    shoulder_point: CartesianPoint
    knee_point: CartesianPoint
    virtual_sphere_center: CartesianPoint
    platform_attachment_point: CartesianPoint


@dataclass(frozen=True, slots=True)
class ForwardKinematicsResult:
    """Selected platform pose plus both mathematical sphere candidates."""

    angles: JointAngles
    position: CartesianPosition
    position_candidates: tuple[CartesianPosition, CartesianPosition]
    arm_poses: tuple[ArmForwardPose, ArmForwardPose, ArmForwardPose]


def _as_vector(point: CartesianPoint) -> Vector3:
    return (point.x_m, point.y_m, point.z_m)


def _add(left: Vector3, right: Vector3) -> Vector3:
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def _subtract(left: Vector3, right: Vector3) -> Vector3:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _scale(vector: Vector3, scalar: float) -> Vector3:
    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _dot(left: Vector3, right: Vector3) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _cross(left: Vector3, right: Vector3) -> Vector3:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _norm(vector: Vector3) -> float:
    return math.sqrt(_dot(vector, vector))


def _unit(vector: Vector3, norm: float) -> Vector3:
    return _scale(vector, 1.0 / norm)


def _position(vector: Vector3) -> CartesianPosition:
    return CartesianPosition(x_m=vector[0], y_m=vector[1], z_m=vector[2])


def intersect_three_equal_spheres(
    center_1: CartesianPoint,
    center_2: CartesianPoint,
    center_3: CartesianPoint,
    radius_m: float,
) -> tuple[CartesianPosition, CartesianPosition]:
    """Return both intersections of three non-degenerate equal-radius spheres."""

    centers = (_as_vector(center_1), _as_vector(center_2), _as_vector(center_3))
    if not math.isfinite(radius_m) or radius_m <= 0.0:
        raise DegenerateSphereGeometryError("sphere radius must be finite and greater than zero")
    if not all(math.isfinite(component) for center in centers for component in center):
        raise DegenerateSphereGeometryError("sphere centers must be finite")

    center_1_vector, center_2_vector, center_3_vector = centers
    center_1_to_2 = _subtract(center_2_vector, center_1_vector)
    center_1_to_3 = _subtract(center_3_vector, center_1_vector)
    distance_1_to_2 = _norm(center_1_to_2)
    length_scale = max(radius_m, distance_1_to_2, _norm(center_1_to_3))
    length_tolerance = GEOMETRIC_RELATIVE_TOLERANCE * length_scale
    if distance_1_to_2 <= length_tolerance:
        raise DegenerateSphereGeometryError("first two sphere centers are coincident")

    basis_x = _unit(center_1_to_2, distance_1_to_2)
    projection_i = _dot(basis_x, center_1_to_3)
    orthogonal_1_to_3 = _subtract(center_1_to_3, _scale(basis_x, projection_i))
    projection_j = _norm(orthogonal_1_to_3)
    if projection_j <= length_tolerance:
        raise DegenerateSphereGeometryError("sphere centers are collinear")

    basis_y = _unit(orthogonal_1_to_3, projection_j)
    basis_z = _cross(basis_x, basis_y)
    coordinate_x = distance_1_to_2 / 2.0
    coordinate_y = (
        projection_i * projection_i
        + projection_j * projection_j
        - 2.0 * projection_i * coordinate_x
    ) / (2.0 * projection_j)
    height_squared = radius_m * radius_m - coordinate_x**2 - coordinate_y**2
    squared_scale = max(radius_m * radius_m, coordinate_x**2, coordinate_y**2)
    squared_tolerance = GEOMETRIC_RELATIVE_TOLERANCE * squared_scale
    if height_squared < -squared_tolerance:
        raise UnreachableAnglesError("three lower-link spheres have no common point")
    if abs(height_squared) <= squared_tolerance:
        raise DegenerateSphereGeometryError("three spheres meet at a tangent boundary")

    plane_point = _add(
        center_1_vector,
        _add(_scale(basis_x, coordinate_x), _scale(basis_y, coordinate_y)),
    )
    height = math.sqrt(height_squared)
    offset = _scale(basis_z, height)
    return (_position(_add(plane_point, offset)), _position(_subtract(plane_point, offset)))


def _angle_values(angles: JointAngles) -> tuple[float, float, float]:
    return (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad)


def _validate_inputs(
    geometry: DeltaGeometry,
    angles: JointAngles,
    assembly_mode: AssemblyMode,
) -> tuple[float, float, float]:
    values = _angle_values(angles)
    if not all(math.isfinite(value) for value in values):
        raise InvalidAnglesError("joint angles must be finite")
    if assembly_mode is not AssemblyMode.KNEE_OUT_PLATFORM_BELOW:
        raise UnsupportedAssemblyModeError(f"unsupported assembly mode: {assembly_mode!r}")

    outward_tolerance_m = GEOMETRIC_RELATIVE_TOLERANCE * geometry.upper_arm_length_m
    for arm_index, angle_rad in enumerate(values, start=1):
        if not geometry.min_joint_angle_rad <= angle_rad <= geometry.max_joint_angle_rad:
            raise JointLimitError(
                f"arm {arm_index} angle {angle_rad} rad is outside "
                f"[{geometry.min_joint_angle_rad}, {geometry.max_joint_angle_rad}] rad"
            )
        if geometry.upper_arm_length_m * math.cos(angle_rad) <= outward_tolerance_m:
            raise AssemblyConstraintError(
                f"arm {arm_index} angle does not satisfy the knee-out assembly branch"
            )
    return values


def forward_kinematics(
    geometry: DeltaGeometry,
    angles: JointAngles,
    assembly_mode: AssemblyMode,
) -> ForwardKinematicsResult:
    """Solve platform-center position from three actuated shoulder angles."""

    angle_values = _validate_inputs(geometry, angles, assembly_mode)
    sphere_centers = tuple(
        virtual_sphere_center(geometry, arm_index, angle_rad)
        for arm_index, angle_rad in enumerate(angle_values, start=1)
    )
    candidates = intersect_three_equal_spheres(
        sphere_centers[0],
        sphere_centers[1],
        sphere_centers[2],
        geometry.lower_arm_length_m,
    )

    assembly_plane_tolerance_m = GEOMETRIC_RELATIVE_TOLERANCE * max(
        geometry.upper_arm_length_m,
        geometry.lower_arm_length_m,
        geometry.base_joint_radius_m,
        geometry.platform_joint_radius_m,
    )
    below_base = tuple(
        candidate for candidate in candidates if candidate.z_m < -assembly_plane_tolerance_m
    )
    if len(below_base) != 1:
        raise AmbiguousForwardSolutionError(
            f"found {len(below_base)} below-base sphere candidates; expected exactly one"
        )
    selected = below_base[0]

    arm_poses = tuple(
        ArmForwardPose(
            arm_index=arm_index,
            shoulder_point=shoulder_point(geometry, arm_index),
            knee_point=knee_point(geometry, arm_index, angle_rad),
            virtual_sphere_center=sphere_centers[arm_index - 1],
            platform_attachment_point=platform_attachment_point(
                geometry,
                selected,
                arm_index,
            ),
        )
        for arm_index, angle_rad in enumerate(angle_values, start=1)
    )
    return ForwardKinematicsResult(
        angles=angles,
        position=selected,
        position_candidates=candidates,
        arm_poses=(arm_poses[0], arm_poses[1], arm_poses[2]),
    )
