"""First configurable rigid-load model for P1 drive sizing."""

import math
from dataclasses import dataclass

import numpy as np

from delta_model.differential_kinematics import (
    CartesianAcceleration,
    DifferentialKinematicsResult,
    JointAccelerations,
)
from delta_model.trajectory import Trajectory, TrajectorySample

STANDARD_GRAVITY_M_S2 = 9.80665
DESIGN_FACTOR = 1.30
TRANSMISSION_EFFICIENCY = 0.90


@dataclass(frozen=True, slots=True)
class DynamicMassCase:
    """Configurable masses for the endpoint-lumped first dynamic model."""

    case_id: str
    payload_kg: float
    platform_tooling_kg: float
    upper_arm_each_kg: float
    lower_assemblies_total_kg: float

    def __post_init__(self) -> None:
        values = (
            self.payload_kg,
            self.platform_tooling_kg,
            self.upper_arm_each_kg,
            self.lower_assemblies_total_kg,
        )
        if not self.case_id.strip():
            raise ValueError("case_id must not be empty")
        if not all(math.isfinite(value) and value >= 0.0 for value in values):
            raise ValueError("dynamic masses must be finite and non-negative")

    @property
    def translating_mass_kg(self) -> float:
        return self.payload_kg + self.platform_tooling_kg + self.lower_assemblies_total_kg / 2.0

    @property
    def knee_share_each_kg(self) -> float:
        return self.lower_assemblies_total_kg / 6.0


NOMINAL_MASS_CASE = DynamicMassCase(
    case_id="nominal_0_30kg_payload",
    payload_kg=0.300,
    platform_tooling_kg=0.250,
    upper_arm_each_kg=0.200,
    lower_assemblies_total_kg=0.300,
)
CONSERVATIVE_MASS_CASE = DynamicMassCase(
    case_id="conservative_0_50kg_payload",
    payload_kg=0.500,
    platform_tooling_kg=0.300,
    upper_arm_each_kg=0.250,
    lower_assemblies_total_kg=0.360,
)


@dataclass(frozen=True, slots=True)
class AxisDynamicSummary:
    """Load-side extrema and RMS torque for one actuated axis."""

    peak_abs_torque_nm: float
    rms_torque_nm: float
    peak_time_s: float
    peak_position_m: tuple[float, float, float]
    maximum_abs_speed_rad_s: float
    maximum_abs_acceleration_rad_s2: float


@dataclass(frozen=True, slots=True)
class DynamicCaseResult:
    """All sampled signed torques and their per-axis summaries."""

    mass_case: DynamicMassCase
    times_s: tuple[float, ...]
    torques_nm: tuple[tuple[float, float, float], ...]
    axes: tuple[AxisDynamicSummary, AxisDynamicSummary, AxisDynamicSummary]


@dataclass(frozen=True, slots=True)
class TransmissionRequirement:
    """Motor-side external-load requirement for one idealized belt ratio."""

    ratio: float
    efficiency: float
    maximum_motor_speed_rad_s: float
    maximum_motor_speed_rpm: float
    maximum_motor_acceleration_rad_s2: float
    peak_motor_load_torque_nm: float
    rms_motor_load_torque_nm: float
    specified_peak_motor_torque_nm: float
    specified_rms_motor_torque_nm: float


def _forward_velocity_jacobian(
    differential: DifferentialKinematicsResult,
) -> np.ndarray:
    cartesian_matrix = np.asarray(differential.cartesian_constraint_matrix, dtype=np.float64)
    joint_matrix = np.asarray(differential.joint_constraint_matrix_m, dtype=np.float64)
    return np.linalg.solve(cartesian_matrix, joint_matrix)


def platform_load_torques(
    differential: DifferentialKinematicsResult,
    force_n: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Convert a Cartesian platform force to joint torque by virtual work."""

    if not all(math.isfinite(value) for value in force_n):
        raise ValueError("Cartesian force must be finite")
    jacobian = _forward_velocity_jacobian(differential)
    torques = jacobian.T @ np.asarray(force_n, dtype=np.float64)
    return (float(torques[0]), float(torques[1]), float(torques[2]))


def load_torques_for_state(
    differential: DifferentialKinematicsResult,
    cartesian_acceleration: CartesianAcceleration,
    joint_accelerations: JointAccelerations,
    mass_case: DynamicMassCase,
) -> tuple[float, float, float]:
    """Calculate signed load-side torque from translating and rotating masses."""

    acceleration = (
        cartesian_acceleration.x_m_s2,
        cartesian_acceleration.y_m_s2,
        cartesian_acceleration.z_m_s2,
    )
    if not all(math.isfinite(value) for value in acceleration):
        raise ValueError("Cartesian acceleration must be finite")
    translating_mass = mass_case.translating_mass_kg
    force = (
        translating_mass * acceleration[0],
        translating_mass * acceleration[1],
        translating_mass * (acceleration[2] + STANDARD_GRAVITY_M_S2),
    )
    platform_torques = platform_load_torques(differential, force)
    length = differential.geometry.upper_arm_length_m
    knee_mass = mass_case.knee_share_each_kg
    rotating_inertia = mass_case.upper_arm_each_kg * length * length / 3.0 + (
        knee_mass * length * length
    )
    gravity_coefficient = STANDARD_GRAVITY_M_S2 * length * (
        mass_case.upper_arm_each_kg / 2.0 + knee_mass
    )
    angles = differential.inverse_result.angles
    angle_values = (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad)
    acceleration_values = (
        joint_accelerations.theta_1_rad_s2,
        joint_accelerations.theta_2_rad_s2,
        joint_accelerations.theta_3_rad_s2,
    )
    torques = tuple(
        platform_torques[index]
        + rotating_inertia * acceleration_values[index]
        - gravity_coefficient * math.cos(angle_values[index])
        for index in range(3)
    )
    return (torques[0], torques[1], torques[2])


def _sample_torque(
    sample: TrajectorySample,
    mass_case: DynamicMassCase,
) -> tuple[float, float, float]:
    return load_torques_for_state(
        sample.differential,
        sample.cartesian.acceleration,
        sample.joint_accelerations,
        mass_case,
    )


def _rms(times: tuple[float, ...], values: tuple[float, ...]) -> float:
    integral = sum(
        0.5 * (values[index] ** 2 + values[index + 1] ** 2)
        * (times[index + 1] - times[index])
        for index in range(len(times) - 1)
    )
    duration = times[-1] - times[0]
    return math.sqrt(integral / duration)


def evaluate_dynamic_case(
    trajectory: Trajectory,
    mass_case: DynamicMassCase,
) -> DynamicCaseResult:
    """Evaluate torques and extrema over every trajectory sample."""

    times = tuple(sample.time_s for sample in trajectory.samples)
    torques = tuple(_sample_torque(sample, mass_case) for sample in trajectory.samples)
    speed_rows = tuple(
        (
            sample.joint_rates.theta_1_rad_s,
            sample.joint_rates.theta_2_rad_s,
            sample.joint_rates.theta_3_rad_s,
        )
        for sample in trajectory.samples
    )
    acceleration_rows = tuple(
        (
            sample.joint_accelerations.theta_1_rad_s2,
            sample.joint_accelerations.theta_2_rad_s2,
            sample.joint_accelerations.theta_3_rad_s2,
        )
        for sample in trajectory.samples
    )
    axes: list[AxisDynamicSummary] = []
    for axis_index in range(3):
        axis_torques = tuple(row[axis_index] for row in torques)
        peak_index = max(range(len(axis_torques)), key=lambda index: abs(axis_torques[index]))
        peak_sample = trajectory.samples[peak_index]
        position = peak_sample.cartesian.position
        axes.append(
            AxisDynamicSummary(
                peak_abs_torque_nm=abs(axis_torques[peak_index]),
                rms_torque_nm=_rms(times, axis_torques),
                peak_time_s=times[peak_index],
                peak_position_m=(position.x_m, position.y_m, position.z_m),
                maximum_abs_speed_rad_s=max(abs(row[axis_index]) for row in speed_rows),
                maximum_abs_acceleration_rad_s2=max(
                    abs(row[axis_index]) for row in acceleration_rows
                ),
            )
        )
    return DynamicCaseResult(
        mass_case=mass_case,
        times_s=times,
        torques_nm=torques,
        axes=(axes[0], axes[1], axes[2]),
    )


def transmission_requirement(
    result: DynamicCaseResult,
    *,
    ratio: float,
    efficiency: float = TRANSMISSION_EFFICIENCY,
    design_factor: float = DESIGN_FACTOR,
) -> TransmissionRequirement:
    """Convert worst-axis output load to a motor-side external-load requirement."""

    if not math.isfinite(ratio) or ratio <= 0.0:
        raise ValueError("transmission ratio must be finite and positive")
    if not math.isfinite(efficiency) or not 0.0 < efficiency <= 1.0:
        raise ValueError("transmission efficiency must lie in (0, 1]")
    if not math.isfinite(design_factor) or design_factor < 1.0:
        raise ValueError("design factor must be finite and at least one")
    maximum_joint_speed = max(axis.maximum_abs_speed_rad_s for axis in result.axes)
    maximum_joint_acceleration = max(
        axis.maximum_abs_acceleration_rad_s2 for axis in result.axes
    )
    peak_output_torque = max(axis.peak_abs_torque_nm for axis in result.axes)
    rms_output_torque = max(axis.rms_torque_nm for axis in result.axes)
    peak_motor_load = peak_output_torque / (ratio * efficiency)
    rms_motor_load = rms_output_torque / (ratio * efficiency)
    motor_speed = ratio * maximum_joint_speed
    return TransmissionRequirement(
        ratio=ratio,
        efficiency=efficiency,
        maximum_motor_speed_rad_s=motor_speed,
        maximum_motor_speed_rpm=motor_speed * 60.0 / (2.0 * math.pi),
        maximum_motor_acceleration_rad_s2=ratio * maximum_joint_acceleration,
        peak_motor_load_torque_nm=peak_motor_load,
        rms_motor_load_torque_nm=rms_motor_load,
        specified_peak_motor_torque_nm=design_factor * peak_motor_load,
        specified_rms_motor_torque_nm=design_factor * rms_motor_load,
    )
