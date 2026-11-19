"""Budget transmission candidates and proxy torque-speed envelope screening."""

import math
from dataclasses import asdict, dataclass
from typing import Literal

from delta_model.design_profiles import BUDGET_DEMONSTRATOR_PROFILE
from delta_model.drive_sizing import (
    ALUMINIUM_DENSITY_KG_M3,
    BELT_ESTIMATED_MASS_KG,
    STEEL_DENSITY_KG_M3,
    DriveTransmission,
    TransmissionInertiaModel,
    annular_cylinder_axial_inertia,
    calculate_refined_drive_load,
    solid_cylinder_axial_inertia,
)
from delta_model.dynamics import (
    DESIGN_FACTOR,
    NOMINAL_MASS_CASE,
    DynamicCaseResult,
    DynamicMassCase,
    evaluate_dynamic_case,
)
from delta_model.trajectory import Trajectory, generate_trajectory
from delta_model.transmission import BeltCandidate, pitch_diameter_m, solve_open_belt_geometry

BUDGET_TRANSMISSION_EFFICIENCY = 0.85
POLYMER_DENSITY_KG_M3 = 1270.0
SUPPORTED_INPUT_SHAFT_DIAMETER_M = 0.008
SUPPORTED_INPUT_SHAFT_LENGTH_M = 0.100
BKL3_COUPLING_MASS_KG = 0.027
BKL3_COUPLING_OUTER_DIAMETER_M = 0.025
PAYLOADS_KG = (0.10, 0.15, 0.20, 0.25, 0.30, 0.50)
CYCLE_DURATIONS_S = (1.00, 1.25, 1.50, 2.00, 2.50, 3.00)


@dataclass(frozen=True, slots=True)
class BudgetTransmissionCandidate:
    """Low-cost belt candidate plus traceable construction assumptions."""

    candidate_id: str
    belt: BeltCandidate
    large_pulley_construction: Literal["catalogue_aluminium", "printed_polymer_hubbed"]
    evidence_state: Literal["locally_catalogue_backed", "geometric_estimate_only"]
    radial_load_status: Literal["separately_supported_input_shaft"]

    @property
    def complexity_rank(self) -> int:
        return 0 if self.large_pulley_construction == "catalogue_aluminium" else 1


@dataclass(frozen=True, slots=True)
class BudgetEnvelopeResult:
    """One payload, duration and transmission screen against proxy evidence."""

    transmission_id: str
    payload_kg: float
    cycle_duration_s: float
    status: Literal["rejected_by_proxy", "not_rejected_by_proxy"]
    required_peak_torque_nm: float
    required_rms_torque_nm_by_axis: tuple[float, float, float]
    worst_curve_utilization: float
    worst_axis: int
    worst_time_s: float
    maximum_motor_speed_rpm: float
    maximum_motor_acceleration_rad_s2: float
    peak_belt_tension_difference_n: float
    speed_evidence_exceeded: bool


@dataclass(frozen=True, slots=True)
class ProxyTraceScreen:
    """Worst sample-level comparison with the bounded proxy curve."""

    worst_curve_utilization: float
    worst_axis: int
    worst_sample_index: int
    speed_evidence_exceeded: bool


def _belt_candidate(
    candidate_id: str, large_teeth: int, belt_length_m: float
) -> BeltCandidate:
    return BeltCandidate(
        candidate_id=candidate_id,
        small_teeth=20,
        large_teeth=large_teeth,
        belt_pitch_length_m=belt_length_m,
        belt_width_m=0.015,
        small_pulley_catalogue="HTD 20-5M-15-2F, provisional 8 mm bore",
        large_pulley_catalogue=(
            "HTD 60-5M-15, finish-machined hub"
            if large_teeth == 60
            else None
        ),
        published_rating_available=False,
        published_stock_pair=large_teeth == 60,
    )


BUDGET_TRANSMISSION_CANDIDATES = (
    BudgetTransmissionCandidate(
        "catalogue_20_60_450",
        _belt_candidate("catalogue_20_60_450", 60, 0.450),
        "catalogue_aluminium",
        "locally_catalogue_backed",
        "separately_supported_input_shaft",
    ),
    BudgetTransmissionCandidate(
        "printed_20_80_500",
        _belt_candidate("printed_20_80_500", 80, 0.500),
        "printed_polymer_hubbed",
        "geometric_estimate_only",
        "separately_supported_input_shaft",
    ),
    BudgetTransmissionCandidate(
        "printed_20_100_600",
        _belt_candidate("printed_20_100_600", 100, 0.600),
        "printed_polymer_hubbed",
        "geometric_estimate_only",
        "separately_supported_input_shaft",
    ),
)


def _small_pulley_inertia() -> float:
    return annular_cylinder_axial_inertia(
        outer_diameter_m=0.036,
        inner_diameter_m=0.008,
        length_m=0.0205,
        density_kg_m3=STEEL_DENSITY_KG_M3,
    ) + annular_cylinder_axial_inertia(
        outer_diameter_m=0.023,
        inner_diameter_m=0.008,
        length_m=0.0055,
        density_kg_m3=STEEL_DENSITY_KG_M3,
    )


def _catalogue_large_pulley_inertia() -> float:
    return annular_cylinder_axial_inertia(
        outer_diameter_m=0.09435,
        inner_diameter_m=0.012,
        length_m=0.0205,
        density_kg_m3=ALUMINIUM_DENSITY_KG_M3,
    ) + annular_cylinder_axial_inertia(
        outer_diameter_m=0.050,
        inner_diameter_m=0.012,
        length_m=0.0095,
        density_kg_m3=ALUMINIUM_DENSITY_KG_M3,
    )


def _printed_large_pulley_inertia(teeth: int) -> float:
    outer_diameter = pitch_diameter_m(teeth) - 0.00114
    rim_inner_diameter = outer_diameter - 0.016
    rim = annular_cylinder_axial_inertia(
        outer_diameter_m=outer_diameter,
        inner_diameter_m=rim_inner_diameter,
        length_m=0.0205,
        density_kg_m3=POLYMER_DENSITY_KG_M3,
    )
    web = annular_cylinder_axial_inertia(
        outer_diameter_m=rim_inner_diameter,
        inner_diameter_m=0.040,
        length_m=0.006,
        density_kg_m3=POLYMER_DENSITY_KG_M3,
    )
    hub_mass_kg = 0.080
    hub = 0.5 * hub_mass_kg * ((0.040 / 2.0) ** 2 + (0.012 / 2.0) ** 2)
    return rim + web + hub


def budget_transmission(candidate: BudgetTransmissionCandidate) -> DriveTransmission:
    """Build the common SI transmission model from stated component estimates."""

    belt = candidate.belt
    belt_mass = BELT_ESTIMATED_MASS_KG * belt.belt_pitch_length_m / 0.600
    small_radius = pitch_diameter_m(belt.small_teeth) / 2.0
    large_inertia = (
        _catalogue_large_pulley_inertia()
        if candidate.large_pulley_construction == "catalogue_aluminium"
        else _printed_large_pulley_inertia(belt.large_teeth)
    )
    return DriveTransmission(
        ratio=belt.ratio,
        efficiency=BUDGET_TRANSMISSION_EFFICIENCY,
        small_pulley_pitch_radius_m=small_radius,
        inertia=TransmissionInertiaModel(
            small_pulley_kg_m2=_small_pulley_inertia(),
            input_shaft_kg_m2=solid_cylinder_axial_inertia(
                diameter_m=SUPPORTED_INPUT_SHAFT_DIAMETER_M,
                length_m=SUPPORTED_INPUT_SHAFT_LENGTH_M,
                density_kg_m3=STEEL_DENSITY_KG_M3,
            ),
            coupling_kg_m2=(
                0.5
                * BKL3_COUPLING_MASS_KG
                * (BKL3_COUPLING_OUTER_DIAMETER_M / 2.0) ** 2
            ),
            belt_at_input_kg_m2=belt_mass * small_radius**2,
            large_pulley_kg_m2=large_inertia,
            bushing_kg_m2=0.0,
            output_shaft_kg_m2=solid_cylinder_axial_inertia(
                diameter_m=0.012,
                length_m=0.150,
                density_kg_m3=STEEL_DENSITY_KG_M3,
            ),
        ),
    )


def _available_proxy_torque_nm(speed_rpm: float) -> tuple[float, bool]:
    curve = BUDGET_DEMONSTRATOR_PROFILE.motor.torque_speed_curve
    if speed_rpm > curve.points[-1].speed_rpm:
        return curve.points[-1].torque_nm - curve.digitization_uncertainty_nm, True
    evaluated_speed = max(speed_rpm, curve.points[0].speed_rpm)
    return (
        curve.available_torque_nm(evaluated_speed) - curve.digitization_uncertainty_nm,
        False,
    )


def screen_proxy_trace(
    motor_torques_nm: tuple[tuple[float, float, float], ...],
    motor_speeds_rad_s: tuple[tuple[float, float, float], ...],
    *,
    design_factor: float = DESIGN_FACTOR,
) -> ProxyTraceScreen:
    """Compare arbitrary finite three-axis samples against the proxy curve."""

    if len(motor_torques_nm) != len(motor_speeds_rad_s) or not motor_torques_nm:
        raise ValueError("torque and speed traces must have equal non-zero length")
    if not math.isfinite(design_factor) or design_factor < 1.0:
        raise ValueError("design factor must be finite and at least one")
    worst_utilization = -math.inf
    worst_axis = 0
    worst_index = 0
    speed_exceeded = False
    for sample_index, (torques, speeds) in enumerate(
        zip(motor_torques_nm, motor_speeds_rad_s, strict=True)
    ):
        if not all(math.isfinite(value) for value in (*torques, *speeds)):
            raise ValueError("proxy trace values must be finite")
        for axis_index, (torque, speed) in enumerate(zip(torques, speeds, strict=True)):
            speed_rpm = abs(speed) * 60.0 / (2.0 * math.pi)
            available, exceeded = _available_proxy_torque_nm(speed_rpm)
            speed_exceeded = speed_exceeded or exceeded
            utilization = design_factor * abs(torque) / available
            if utilization > worst_utilization:
                worst_utilization = utilization
                worst_axis = axis_index
                worst_index = sample_index
    return ProxyTraceScreen(
        worst_curve_utilization=worst_utilization,
        worst_axis=worst_axis + 1,
        worst_sample_index=worst_index,
        speed_evidence_exceeded=speed_exceeded,
    )


def _rms(times: tuple[float, ...], values: tuple[float, ...]) -> float:
    integral = sum(
        0.5 * (values[index] ** 2 + values[index + 1] ** 2)
        * (times[index + 1] - times[index])
        for index in range(len(times) - 1)
    )
    return math.sqrt(integral / (times[-1] - times[0]))


def budget_output_load(
    *,
    payload_kg: float,
    cycle_duration_s: float,
) -> tuple[Trajectory, DynamicCaseResult]:
    """Return the budget trajectory and its external load at the output joint."""

    trajectory = generate_trajectory(cycle_time_scale=cycle_duration_s)
    mass_case = DynamicMassCase(
        case_id=f"budget_{payload_kg:.2f}kg",
        payload_kg=payload_kg,
        platform_tooling_kg=NOMINAL_MASS_CASE.platform_tooling_kg,
        upper_arm_each_kg=NOMINAL_MASS_CASE.upper_arm_each_kg,
        lower_assemblies_total_kg=NOMINAL_MASS_CASE.lower_assemblies_total_kg,
    )
    return trajectory, evaluate_dynamic_case(trajectory, mass_case)


def assess_budget_operating_point(
    candidate: BudgetTransmissionCandidate,
    *,
    payload_kg: float,
    cycle_duration_s: float,
) -> BudgetEnvelopeResult:
    """Screen one operating point sample by sample against the proxy curve."""

    trajectory, dynamic = budget_output_load(
        payload_kg=payload_kg, cycle_duration_s=cycle_duration_s
    )
    transmission = budget_transmission(candidate)
    trace = calculate_refined_drive_load(
        trajectory,
        dynamic,
        rotor_inertia_kg_m2=BUDGET_DEMONSTRATOR_PROFILE.motor.rotor_inertia_kg_m2,
        transmission=transmission,
    )
    screen = screen_proxy_trace(trace.motor_torques_nm, trace.motor_speeds_rad_s)
    rms_by_axis = tuple(
        DESIGN_FACTOR
        * _rms(dynamic.times_s, tuple(row[axis_index] for row in trace.motor_torques_nm))
        for axis_index in range(3)
    )
    required_peak = DESIGN_FACTOR * max(
        abs(value) for row in trace.motor_torques_nm for value in row
    )
    peak_belt_tension = max(
        abs(value) for row in trace.belt_torques_nm for value in row
    ) / transmission.small_pulley_pitch_radius_m
    rejected = screen.speed_evidence_exceeded or screen.worst_curve_utilization > 1.0
    return BudgetEnvelopeResult(
        transmission_id=candidate.candidate_id,
        payload_kg=payload_kg,
        cycle_duration_s=cycle_duration_s,
        status="rejected_by_proxy" if rejected else "not_rejected_by_proxy",
        required_peak_torque_nm=required_peak,
        required_rms_torque_nm_by_axis=(rms_by_axis[0], rms_by_axis[1], rms_by_axis[2]),
        worst_curve_utilization=screen.worst_curve_utilization,
        worst_axis=screen.worst_axis,
        worst_time_s=dynamic.times_s[screen.worst_sample_index],
        maximum_motor_speed_rpm=trace.maximum_motor_speed_rpm,
        maximum_motor_acceleration_rad_s2=trace.maximum_motor_acceleration_rad_s2,
        peak_belt_tension_difference_n=peak_belt_tension,
        speed_evidence_exceeded=screen.speed_evidence_exceeded,
    )


def _candidate_document(candidate: BudgetTransmissionCandidate) -> dict[str, object]:
    geometry = solve_open_belt_geometry(candidate.belt)
    transmission = budget_transmission(candidate)
    return {
        **asdict(candidate),
        "complexity_rank": candidate.complexity_rank,
        "geometry": asdict(geometry),
        "transmission": asdict(transmission),
    }


def budget_performance_envelope_document() -> dict[str, object]:
    """Build the deterministic proxy-only ratio/payload/cycle report."""

    results = tuple(
        assess_budget_operating_point(
            candidate,
            payload_kg=payload,
            cycle_duration_s=duration,
        )
        for candidate in BUDGET_TRANSMISSION_CANDIDATES
        for payload in PAYLOADS_KG
        for duration in CYCLE_DURATIONS_S
    )
    fastest: list[dict[str, object]] = []
    for candidate in BUDGET_TRANSMISSION_CANDIDATES:
        for payload in PAYLOADS_KG:
            matches = [
                result.cycle_duration_s
                for result in results
                if result.transmission_id == candidate.candidate_id
                and result.payload_kg == payload
                and result.status == "not_rejected_by_proxy"
            ]
            fastest.append(
                {
                    "transmission_id": candidate.candidate_id,
                    "payload_kg": payload,
                    "fastest_not_rejected_cycle_s": min(matches) if matches else None,
                }
            )
    catalogue_results = [
        result
        for result in results
        if result.transmission_id == "catalogue_20_60_450"
        and result.status == "not_rejected_by_proxy"
    ]
    recommendation = max(
        catalogue_results,
        key=lambda result: (result.payload_kg, -result.cycle_duration_s),
    )
    curve = BUDGET_DEMONSTRATOR_PROFILE.motor.torque_speed_curve
    return {
        "schema": "delta-robot-budget-performance-envelope/v1",
        "status": "proxy_only",
        "motor": {
            "kit_model": BUDGET_DEMONSTRATOR_PROFILE.motor.kit_model,
            "motor_model": BUDGET_DEMONSTRATOR_PROFILE.motor.motor_model,
            "driver_model": BUDGET_DEMONSTRATOR_PROFILE.motor.driver_model,
            "rotor_inertia_kg_m2": BUDGET_DEMONSTRATOR_PROFILE.motor.rotor_inertia_kg_m2,
        },
        "curve_evidence": asdict(curve),
        "screening_policy": {
            "design_factor": DESIGN_FACTOR,
            "low_speed": "0..100 rpm uses 100 rpm running torque minus uncertainty",
            "maximum_evidence_speed_rpm": curve.points[-1].speed_rpm,
            "status_not_rejected_is_not_a_physical_pass": True,
        },
        "mass_baseline_kg": {
            "platform_tooling": NOMINAL_MASS_CASE.platform_tooling_kg,
            "upper_arm_each": NOMINAL_MASS_CASE.upper_arm_each_kg,
            "lower_assemblies_total": NOMINAL_MASS_CASE.lower_assemblies_total_kg,
        },
        "transmission_candidates": [
            _candidate_document(candidate) for candidate in BUDGET_TRANSMISSION_CANDIDATES
        ],
        "results": [asdict(result) for result in results],
        "fastest_not_rejected": fastest,
        "provisional_recommendation": {
            "transmission_id": recommendation.transmission_id,
            "payload_kg": recommendation.payload_kg,
            "cycle_duration_s": recommendation.cycle_duration_s,
            "reason": "simplest locally catalogue-backed candidate at the largest swept payload",
            "status": recommendation.status,
        },
        "blockers": [
            "proxy curve uses CL57T-V41 at 36 V, not the exact CL57Y-V20 kit conditions",
            "supported-jackshaft calculation is digital evidence pending "
            "delivered-part fits and physical P1",
            "budget pulley inertias are estimates pending representative CAD and weighing",
            "temperature and following error require the physical P1 bench",
        ],
    }
