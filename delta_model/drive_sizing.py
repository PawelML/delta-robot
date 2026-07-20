"""Candidate-aware motor sizing including published rotor inertia."""

import math
from dataclasses import dataclass

from delta_model.dynamics import (
    DESIGN_FACTOR,
    TRANSMISSION_EFFICIENCY,
    DynamicCaseResult,
)
from delta_model.trajectory import Trajectory
from delta_model.transmission import inertia_from_wr2_lb_ft2, pitch_diameter_m


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


@dataclass(frozen=True, slots=True)
class TransmissionInertiaModel:
    """Physical component inertias separated by input and output speed."""

    small_pulley_kg_m2: float
    input_shaft_kg_m2: float
    coupling_kg_m2: float
    belt_at_input_kg_m2: float
    large_pulley_kg_m2: float
    bushing_kg_m2: float
    output_shaft_kg_m2: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value) and value >= 0.0
            for value in (
                self.small_pulley_kg_m2,
                self.input_shaft_kg_m2,
                self.coupling_kg_m2,
                self.belt_at_input_kg_m2,
                self.large_pulley_kg_m2,
                self.bushing_kg_m2,
                self.output_shaft_kg_m2,
            )
        ):
            raise ValueError("transmission inertias must be finite and non-negative")

    @property
    def input_total_kg_m2(self) -> float:
        return (
            self.small_pulley_kg_m2
            + self.input_shaft_kg_m2
            + self.coupling_kg_m2
            + self.belt_at_input_kg_m2
        )

    @property
    def output_total_kg_m2(self) -> float:
        return self.large_pulley_kg_m2 + self.bushing_kg_m2 + self.output_shaft_kg_m2


@dataclass(frozen=True, slots=True)
class RefinedAxisAssessment:
    """One-axis result including real transmission component inertia."""

    required_peak_torque_nm: float
    required_rms_torque_nm: float
    peak_torque_utilization: float
    continuous_torque_utilization: float
    peak_belt_tension_difference_n: float


@dataclass(frozen=True, slots=True)
class RefinedDriveAssessment:
    """Time-domain drive result including transmission and rotor inertia."""

    ratio: float
    efficiency: float
    design_factor: float
    axes: tuple[RefinedAxisAssessment, RefinedAxisAssessment, RefinedAxisAssessment]
    motor_torques_nm: tuple[tuple[float, float, float], ...]
    belt_torques_nm: tuple[tuple[float, float, float], ...]
    maximum_motor_speed_rpm: float
    maximum_motor_acceleration_rad_s2: float
    maximum_belt_power_w: float
    passes: bool


STEEL_DENSITY_KG_M3 = 7850.0
ALUMINIUM_DENSITY_KG_M3 = 2700.0
BELT_ESTIMATED_MASS_KG = 0.01715


def _solid_cylinder_axial_inertia(
    *, diameter_m: float, length_m: float, density_kg_m3: float
) -> float:
    radius = diameter_m / 2.0
    mass = math.pi * radius**2 * length_m * density_kg_m3
    return 0.5 * mass * radius**2


def _annular_cylinder_axial_inertia(
    *, outer_diameter_m: float, inner_diameter_m: float, length_m: float, density_kg_m3: float
) -> float:
    outer_radius = outer_diameter_m / 2.0
    inner_radius = inner_diameter_m / 2.0
    mass = math.pi * (outer_radius**2 - inner_radius**2) * length_m * density_kg_m3
    return 0.5 * mass * (outer_radius**2 + inner_radius**2)


P1_TRANSMISSION_INERTIA = TransmissionInertiaModel(
    small_pulley_kg_m2=inertia_from_wr2_lb_ft2(0.000097),
    input_shaft_kg_m2=_solid_cylinder_axial_inertia(
        diameter_m=0.009525, length_m=0.110, density_kg_m3=STEEL_DENSITY_KG_M3
    ),
    coupling_kg_m2=_annular_cylinder_axial_inertia(
        outer_diameter_m=0.035,
        inner_diameter_m=0.009525,
        length_m=0.045,
        density_kg_m3=ALUMINIUM_DENSITY_KG_M3,
    ),
    belt_at_input_kg_m2=BELT_ESTIMATED_MASS_KG * (pitch_diameter_m(18) / 2.0) ** 2,
    large_pulley_kg_m2=inertia_from_wr2_lb_ft2(0.1358),
    bushing_kg_m2=_annular_cylinder_axial_inertia(
        outer_diameter_m=0.057,
        inner_diameter_m=0.020,
        length_m=0.0254,
        density_kg_m3=STEEL_DENSITY_KG_M3,
    ),
    output_shaft_kg_m2=_solid_cylinder_axial_inertia(
        diameter_m=0.020, length_m=0.180, density_kg_m3=STEEL_DENSITY_KG_M3
    ),
)


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


def assess_refined_drive(
    trajectory: Trajectory,
    dynamic_result: DynamicCaseResult,
    candidate: MotorCandidate,
    transmission: TransmissionInertiaModel = P1_TRANSMISSION_INERTIA,
    *,
    ratio: float = 5.0,
    efficiency: float = TRANSMISSION_EFFICIENCY,
    design_factor: float = DESIGN_FACTOR,
) -> RefinedDriveAssessment:
    """Add input/output transmission and rotor inertia at every trajectory sample."""

    if len(trajectory.samples) != len(dynamic_result.torques_nm):
        raise ValueError("trajectory and dynamic result sample counts must match")
    if ratio <= 0.0 or not 0.0 < efficiency <= 1.0 or design_factor < 1.0:
        raise ValueError("ratio, efficiency or design factor is invalid")
    radius = pitch_diameter_m(18) / 2.0
    motor_rows: list[tuple[float, float, float]] = []
    belt_rows: list[tuple[float, float, float]] = []
    speed_rows: list[tuple[float, float, float]] = []
    acceleration_rows: list[tuple[float, float, float]] = []
    for sample, output_torques in zip(
        trajectory.samples, dynamic_result.torques_nm, strict=True
    ):
        joint_accelerations = (
            sample.joint_accelerations.theta_1_rad_s2,
            sample.joint_accelerations.theta_2_rad_s2,
            sample.joint_accelerations.theta_3_rad_s2,
        )
        joint_speeds = (
            sample.joint_rates.theta_1_rad_s,
            sample.joint_rates.theta_2_rad_s,
            sample.joint_rates.theta_3_rad_s,
        )
        belt_torques = tuple(
            (output_torque + transmission.output_total_kg_m2 * acceleration)
            / (ratio * efficiency)
            for output_torque, acceleration in zip(
                output_torques, joint_accelerations, strict=True
            )
        )
        motor_torques = tuple(
            belt_torque
            + (transmission.input_total_kg_m2 + candidate.rotor_inertia_kg_m2)
            * ratio
            * acceleration
            for belt_torque, acceleration in zip(
                belt_torques, joint_accelerations, strict=True
            )
        )
        motor_rows.append((motor_torques[0], motor_torques[1], motor_torques[2]))
        belt_rows.append((belt_torques[0], belt_torques[1], belt_torques[2]))
        speed_rows.append(
            (ratio * joint_speeds[0], ratio * joint_speeds[1], ratio * joint_speeds[2])
        )
        acceleration_rows.append(
            (
                ratio * joint_accelerations[0],
                ratio * joint_accelerations[1],
                ratio * joint_accelerations[2],
            )
        )
    axes: list[RefinedAxisAssessment] = []
    for axis_index in range(3):
        torques = tuple(row[axis_index] for row in motor_rows)
        belt_torques = tuple(row[axis_index] for row in belt_rows)
        required_peak = design_factor * max(abs(value) for value in torques)
        required_rms = design_factor * _rms(dynamic_result.times_s, torques)
        axes.append(
            RefinedAxisAssessment(
                required_peak_torque_nm=required_peak,
                required_rms_torque_nm=required_rms,
                peak_torque_utilization=required_peak / candidate.peak_torque_nm,
                continuous_torque_utilization=required_rms / candidate.rated_torque_nm,
                peak_belt_tension_difference_n=max(abs(value) for value in belt_torques)
                / radius,
            )
        )
    maximum_speed_rad_s = max(abs(value) for row in speed_rows for value in row)
    maximum_acceleration = max(
        abs(value) for row in acceleration_rows for value in row
    )
    maximum_power = max(
        abs(torque * speed)
        for torque_row, speed_row in zip(belt_rows, speed_rows, strict=True)
        for torque, speed in zip(torque_row, speed_row, strict=True)
    )
    maximum_speed_rpm = maximum_speed_rad_s * 60.0 / (2.0 * math.pi)
    passes = (
        max(axis.required_peak_torque_nm for axis in axes) <= candidate.peak_torque_nm
        and max(axis.required_rms_torque_nm for axis in axes) <= candidate.rated_torque_nm
        and maximum_speed_rpm <= candidate.rated_speed_rpm
    )
    return RefinedDriveAssessment(
        ratio=ratio,
        efficiency=efficiency,
        design_factor=design_factor,
        axes=(axes[0], axes[1], axes[2]),
        motor_torques_nm=tuple(motor_rows),
        belt_torques_nm=tuple(belt_rows),
        maximum_motor_speed_rpm=maximum_speed_rpm,
        maximum_motor_acceleration_rad_s2=maximum_acceleration,
        maximum_belt_power_w=maximum_power,
        passes=passes,
    )
