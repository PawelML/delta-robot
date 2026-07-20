"""Velocity mappings and singularity margins for the rotary delta robot."""

import math
import sys
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from delta_model.arm_geometry import arm_radial_vector
from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.geometry import DeltaGeometry
from delta_model.inverse_kinematics import InverseKinematicsResult, inverse_kinematics

SINGULAR_VALUE_RELATIVE_TOLERANCE = 64.0 * sys.float_info.epsilon
PRACTICALLY_USABLE_MARGIN = 0.20

Matrix3 = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


class DifferentialKinematicsError(ValueError):
    """Base class for velocity-level failures."""


class InvalidVelocityError(DifferentialKinematicsError):
    """Raised when a requested Cartesian or joint velocity is not finite."""


class SingularDifferentialKinematicsError(DifferentialKinematicsError):
    """Raised when a requested velocity mapping requires a singular solve."""


@dataclass(frozen=True, slots=True)
class CartesianVelocity:
    """Platform-center velocity in the base frame, expressed in metres per second."""

    x_m_s: float
    y_m_s: float
    z_m_s: float


@dataclass(frozen=True, slots=True)
class CartesianAcceleration:
    """Platform-center acceleration in the base frame, in metres per second squared."""

    x_m_s2: float
    y_m_s2: float
    z_m_s2: float


@dataclass(frozen=True, slots=True)
class JointRates:
    """Actuated shoulder rates in arm order, expressed in radians per second."""

    theta_1_rad_s: float
    theta_2_rad_s: float
    theta_3_rad_s: float


@dataclass(frozen=True, slots=True)
class JointAccelerations:
    """Actuated shoulder accelerations in arm order, in radians per second squared."""

    theta_1_rad_s2: float
    theta_2_rad_s2: float
    theta_3_rad_s2: float


@dataclass(frozen=True, slots=True)
class SingularityMetrics:
    """Dimensionless mechanism-quality metrics; zero denotes singularity."""

    parallel_margin: float
    serial_margin: float
    singularity_margin: float
    serial_margin_by_arm: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class DifferentialKinematicsResult:
    """Matrices, metrics and solved pose at one platform position."""

    geometry: DeltaGeometry
    position: CartesianPosition
    inverse_result: InverseKinematicsResult
    cartesian_constraint_matrix: Matrix3
    joint_constraint_matrix_m: Matrix3
    metrics: SingularityMetrics


def _as_matrix3(matrix: npt.NDArray[np.float64]) -> Matrix3:
    return (
        (float(matrix[0, 0]), float(matrix[0, 1]), float(matrix[0, 2])),
        (float(matrix[1, 0]), float(matrix[1, 1]), float(matrix[1, 2])),
        (float(matrix[2, 0]), float(matrix[2, 1]), float(matrix[2, 2])),
    )


def _matrices(result: DifferentialKinematicsResult) -> tuple[
    npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    return (
        np.asarray(result.cartesian_constraint_matrix, dtype=np.float64),
        np.asarray(result.joint_constraint_matrix_m, dtype=np.float64),
    )


def differential_kinematics(
    geometry: DeltaGeometry,
    position: CartesianPosition,
    assembly_mode: AssemblyMode,
) -> DifferentialKinematicsResult:
    """Differentiate rigid lower-link constraints and calculate quality margins."""

    inverse_result = inverse_kinematics(geometry, position, assembly_mode)
    lower_length = geometry.lower_arm_length_m
    upper_length = geometry.upper_arm_length_m
    cartesian_rows: list[tuple[float, float, float]] = []
    joint_diagonal_m: list[float] = []

    for arm in inverse_result.arm_solutions:
        lower_vector = np.asarray(
            (
                arm.platform_attachment_point.x_m - arm.knee_point.x_m,
                arm.platform_attachment_point.y_m - arm.knee_point.y_m,
                arm.platform_attachment_point.z_m - arm.knee_point.z_m,
            ),
            dtype=np.float64,
        )
        cartesian_rows.append(
            (
                float(lower_vector[0] / lower_length),
                float(lower_vector[1] / lower_length),
                float(lower_vector[2] / lower_length),
            )
        )
        radial_x, radial_y = arm_radial_vector(arm.arm_index)
        sine = math.sin(arm.angle_rad)
        cosine = math.cos(arm.angle_rad)
        knee_derivative = np.asarray(
            (
                -upper_length * sine * radial_x,
                -upper_length * sine * radial_y,
                -upper_length * cosine,
            ),
            dtype=np.float64,
        )
        joint_diagonal_m.append(float(np.dot(lower_vector, knee_derivative) / lower_length))

    cartesian_matrix = np.asarray(cartesian_rows, dtype=np.float64)
    joint_matrix = np.diag(np.asarray(joint_diagonal_m, dtype=np.float64))
    singular_values = np.linalg.svd(cartesian_matrix, compute_uv=False)
    sigma_max = float(singular_values[0])
    sigma_min = float(singular_values[-1])
    parallel_margin = 0.0 if sigma_max == 0.0 else sigma_min / sigma_max
    serial_by_arm = tuple(abs(value) / upper_length for value in joint_diagonal_m)
    serial_margin = min(serial_by_arm)
    singularity_margin = min(parallel_margin, serial_margin)
    metrics = SingularityMetrics(
        parallel_margin=parallel_margin,
        serial_margin=serial_margin,
        singularity_margin=singularity_margin,
        serial_margin_by_arm=(serial_by_arm[0], serial_by_arm[1], serial_by_arm[2]),
    )
    return DifferentialKinematicsResult(
        geometry=geometry,
        position=position,
        inverse_result=inverse_result,
        cartesian_constraint_matrix=_as_matrix3(cartesian_matrix),
        joint_constraint_matrix_m=_as_matrix3(joint_matrix),
        metrics=metrics,
    )


def joint_rates_for_cartesian_velocity(
    result: DifferentialKinematicsResult,
    velocity: CartesianVelocity,
) -> JointRates:
    """Map platform velocity to motor rates, rejecting a serial singularity."""

    values = (velocity.x_m_s, velocity.y_m_s, velocity.z_m_s)
    if not all(math.isfinite(value) for value in values):
        raise InvalidVelocityError("Cartesian velocity components must be finite")
    cartesian_matrix, joint_matrix = _matrices(result)
    diagonal = np.diag(joint_matrix)
    scale = max(float(np.max(np.abs(diagonal))), sys.float_info.min)
    tolerance = SINGULAR_VALUE_RELATIVE_TOLERANCE * scale
    if bool(np.any(np.abs(diagonal) <= tolerance)):
        raise SingularDifferentialKinematicsError("joint constraint matrix is serial-singular")
    right_hand_side = cartesian_matrix @ np.asarray(values, dtype=np.float64)
    rates = right_hand_side / diagonal
    return JointRates(float(rates[0]), float(rates[1]), float(rates[2]))


def cartesian_velocity_for_joint_rates(
    result: DifferentialKinematicsResult,
    rates: JointRates,
) -> CartesianVelocity:
    """Map motor rates to platform velocity, rejecting a parallel singularity."""

    values = (rates.theta_1_rad_s, rates.theta_2_rad_s, rates.theta_3_rad_s)
    if not all(math.isfinite(value) for value in values):
        raise InvalidVelocityError("joint-rate components must be finite")
    cartesian_matrix, joint_matrix = _matrices(result)
    singular_values = np.linalg.svd(cartesian_matrix, compute_uv=False)
    tolerance = SINGULAR_VALUE_RELATIVE_TOLERANCE * float(singular_values[0])
    if float(singular_values[-1]) <= tolerance:
        raise SingularDifferentialKinematicsError(
            "Cartesian constraint matrix is parallel-singular"
        )
    right_hand_side = joint_matrix @ np.asarray(values, dtype=np.float64)
    velocity = np.linalg.solve(cartesian_matrix, right_hand_side)
    return CartesianVelocity(float(velocity[0]), float(velocity[1]), float(velocity[2]))


def joint_accelerations_for_cartesian_motion(
    result: DifferentialKinematicsResult,
    velocity: CartesianVelocity,
    acceleration: CartesianAcceleration,
    rates: JointRates | None = None,
) -> JointAccelerations:
    """Map Cartesian motion derivatives to exact joint accelerations."""

    velocity_values = (velocity.x_m_s, velocity.y_m_s, velocity.z_m_s)
    acceleration_values = (
        acceleration.x_m_s2,
        acceleration.y_m_s2,
        acceleration.z_m_s2,
    )
    if not all(math.isfinite(value) for value in (*velocity_values, *acceleration_values)):
        raise InvalidVelocityError("Cartesian velocity and acceleration components must be finite")
    solved_rates = rates or joint_rates_for_cartesian_velocity(result, velocity)
    rate_values = (
        solved_rates.theta_1_rad_s,
        solved_rates.theta_2_rad_s,
        solved_rates.theta_3_rad_s,
    )
    if not all(math.isfinite(value) for value in rate_values):
        raise InvalidVelocityError("joint-rate components must be finite")

    _, joint_matrix = _matrices(result)
    diagonal = np.diag(joint_matrix)
    scale = max(float(np.max(np.abs(diagonal))), sys.float_info.min)
    tolerance = SINGULAR_VALUE_RELATIVE_TOLERANCE * scale
    if bool(np.any(np.abs(diagonal) <= tolerance)):
        raise SingularDifferentialKinematicsError("joint constraint matrix is serial-singular")

    geometry = result.geometry
    lower_length = geometry.lower_arm_length_m
    upper_length = geometry.upper_arm_length_m
    cartesian_velocity = np.asarray(velocity_values, dtype=np.float64)
    cartesian_acceleration = np.asarray(acceleration_values, dtype=np.float64)
    joint_accelerations: list[float] = []
    for arm, rate, joint_diagonal in zip(
        result.inverse_result.arm_solutions,
        rate_values,
        diagonal,
        strict=True,
    ):
        radial_x, radial_y = arm_radial_vector(arm.arm_index)
        sine = math.sin(arm.angle_rad)
        cosine = math.cos(arm.angle_rad)
        lower_vector = np.asarray(
            (
                arm.platform_attachment_point.x_m - arm.knee_point.x_m,
                arm.platform_attachment_point.y_m - arm.knee_point.y_m,
                arm.platform_attachment_point.z_m - arm.knee_point.z_m,
            ),
            dtype=np.float64,
        )
        knee_first = np.asarray(
            (
                -upper_length * sine * radial_x,
                -upper_length * sine * radial_y,
                -upper_length * cosine,
            ),
            dtype=np.float64,
        )
        knee_second = np.asarray(
            (
                -upper_length * cosine * radial_x,
                -upper_length * cosine * radial_y,
                upper_length * sine,
            ),
            dtype=np.float64,
        )
        lower_rate = cartesian_velocity - knee_first * rate
        right_hand_side = (
            float(np.dot(lower_vector, cartesian_acceleration))
            + float(np.dot(lower_rate, lower_rate))
            - float(np.dot(lower_vector, knee_second)) * rate * rate
        ) / lower_length
        joint_accelerations.append(right_hand_side / float(joint_diagonal))
    return JointAccelerations(
        joint_accelerations[0],
        joint_accelerations[1],
        joint_accelerations[2],
    )
