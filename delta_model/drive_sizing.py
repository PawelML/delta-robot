"""Candidate-aware motor sizing including published rotor inertia."""

import math
from dataclasses import dataclass

from delta_model.dynamics import (
    DESIGN_FACTOR,
    TRANSMISSION_EFFICIENCY,
    DynamicCaseResult,
)
from delta_model.trajectory import Trajectory


@dataclass(frozen=True, slots=True)
class MotorCandidate:
    """Primary-source motor values needed by the first sizing check."""

    model: str
    rated_torque_nm: float
    peak_torque_nm: float
    rated_speed_rpm: float
    maximum_speed_rpm: float
    rotor_inertia_kg_m2: float
    rated_voltage_vdc: float
    continuous_current_a_rms: float
    peak_current_a: float
    encoder_bits: int
    source_url: str


LEADSHINE_ISV2_RS6040V48G = MotorCandidate(
    model="Leadshine iSV2-RS6040V48G",
    rated_torque_nm=1.27,
    peak_torque_nm=3.81,
    rated_speed_rpm=3000.0,
    maximum_speed_rpm=4000.0,
    rotor_inertia_kg_m2=0.58e-4,
    rated_voltage_vdc=48.0,
    continuous_current_a_rms=10.0,
    peak_current_a=28.0,
    encoder_bits=17,
    source_url="https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html",
)


@dataclass(frozen=True, slots=True)
class CandidateAxisAssessment:
    """Worst candidate load on one axis after the design factor."""

    required_peak_torque_nm: float
    required_rms_torque_nm: float
    peak_torque_utilization: float
    continuous_torque_utilization: float


@dataclass(frozen=True, slots=True)
class MotorCandidateAssessment:
    """Three-axis numerical screen for one motor and ratio."""

    candidate: MotorCandidate
    ratio: float
    efficiency: float
    design_factor: float
    maximum_motor_speed_rpm: float
    maximum_motor_acceleration_rad_s2: float
    axes: tuple[
        CandidateAxisAssessment,
        CandidateAxisAssessment,
        CandidateAxisAssessment,
    ]
    passes: bool


def _rms(times: tuple[float, ...], values: tuple[float, ...]) -> float:
    integral = sum(
        0.5 * (values[index] ** 2 + values[index + 1] ** 2)
        * (times[index + 1] - times[index])
        for index in range(len(times) - 1)
    )
    return math.sqrt(integral / (times[-1] - times[0]))


def assess_motor_candidate(
    trajectory: Trajectory,
    dynamic_result: DynamicCaseResult,
    candidate: MotorCandidate,
    *,
    ratio: float = 5.0,
    efficiency: float = TRANSMISSION_EFFICIENCY,
    design_factor: float = DESIGN_FACTOR,
) -> MotorCandidateAssessment:
    """Add motor rotor inertia sample by sample and compare ratings."""

    if len(trajectory.samples) != len(dynamic_result.torques_nm):
        raise ValueError("trajectory and dynamic result sample counts must match")
    if ratio <= 0.0 or not 0.0 < efficiency <= 1.0 or design_factor < 1.0:
        raise ValueError("ratio, efficiency or design factor is invalid")
    acceleration_rows = tuple(
        (
            sample.joint_accelerations.theta_1_rad_s2,
            sample.joint_accelerations.theta_2_rad_s2,
            sample.joint_accelerations.theta_3_rad_s2,
        )
        for sample in trajectory.samples
    )
    speed_rows = tuple(
        (
            sample.joint_rates.theta_1_rad_s,
            sample.joint_rates.theta_2_rad_s,
            sample.joint_rates.theta_3_rad_s,
        )
        for sample in trajectory.samples
    )
    axes: list[CandidateAxisAssessment] = []
    for axis_index in range(3):
        motor_torques = tuple(
            output_torque[axis_index] / (ratio * efficiency)
            + candidate.rotor_inertia_kg_m2 * ratio * accelerations[axis_index]
            for output_torque, accelerations in zip(
                dynamic_result.torques_nm,
                acceleration_rows,
                strict=True,
            )
        )
        required_peak = design_factor * max(abs(value) for value in motor_torques)
        required_rms = design_factor * _rms(dynamic_result.times_s, motor_torques)
        axes.append(
            CandidateAxisAssessment(
                required_peak_torque_nm=required_peak,
                required_rms_torque_nm=required_rms,
                peak_torque_utilization=required_peak / candidate.peak_torque_nm,
                continuous_torque_utilization=required_rms / candidate.rated_torque_nm,
            )
        )
    maximum_speed_rad_s = ratio * max(
        abs(value) for row in speed_rows for value in row
    )
    maximum_acceleration = ratio * max(
        abs(value) for row in acceleration_rows for value in row
    )
    maximum_speed_rpm = maximum_speed_rad_s * 60.0 / (2.0 * math.pi)
    passes = (
        max(axis.required_peak_torque_nm for axis in axes) <= candidate.peak_torque_nm
        and max(axis.required_rms_torque_nm for axis in axes) <= candidate.rated_torque_nm
        and maximum_speed_rpm <= candidate.rated_speed_rpm
    )
    return MotorCandidateAssessment(
        candidate=candidate,
        ratio=ratio,
        efficiency=efficiency,
        design_factor=design_factor,
        maximum_motor_speed_rpm=maximum_speed_rpm,
        maximum_motor_acceleration_rad_s2=maximum_acceleration,
        axes=(axes[0], axes[1], axes[2]),
        passes=passes,
    )
