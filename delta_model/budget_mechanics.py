"""Mechanical closure calculations for the selected budget transmission."""

import math
from dataclasses import asdict, dataclass

from delta_model.budget_sizing import (
    BKL3_COUPLING_MASS_KG,
    BKL3_COUPLING_OUTER_DIAMETER_M,
    BUDGET_TRANSMISSION_CANDIDATES,
    SUPPORTED_INPUT_SHAFT_DIAMETER_M,
    SUPPORTED_INPUT_SHAFT_LENGTH_M,
    assess_budget_operating_point,
    budget_transmission,
)
from delta_model.dynamics import DESIGN_FACTOR
from delta_model.transmission import solve_open_belt_geometry

LBF_TO_N = 4.4482216152605
GATES_5M_15_MIN_INSTALLATION_TENSION_N = 13.5 * LBF_TO_N
MOTOR_DYNAMIC_RADIAL_LIMIT_N = 75.0
INPUT_BEARING_SPAN_M = 0.050
SKF_608_DYNAMIC_RATING_N = 3320.0
BKL3_RATED_TORQUE_NM = 3.0
PROVISIONAL_C45_YIELD_STRENGTH_PA = 300.0e6
KEYWAY_FATIGUE_STRESS_MULTIPLIER = 1.50


@dataclass(frozen=True, slots=True)
class BeltRadialLoad:
    """Two-span pulley force result in newtons."""

    effective_tension_difference_n: float
    installation_tension_per_span_n: float
    span_included_angle_rad: float
    tight_span_tension_n: float
    slack_span_tension_n: float
    resultant_radial_load_n: float


@dataclass(frozen=True, slots=True)
class SupportedShaftScreen:
    """Conservative simply-supported shaft and bearing screen."""

    shaft_diameter_m: float
    bearing_span_m: float
    radial_load_n: float
    reaction_per_bearing_n: float
    maximum_bending_moment_nm: float
    design_torque_nm: float
    nominal_bending_stress_pa: float
    nominal_torsional_shear_pa: float
    factored_von_mises_stress_pa: float
    provisional_yield_strength_pa: float
    yield_safety_factor: float
    bearing_dynamic_rating_n: float
    bearing_rating_utilization: float
    coupling_rated_torque_nm: float
    coupling_torque_factor: float


def _positive_finite(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")


def _nonnegative_finite(name: str, value: float) -> None:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative")


def calculate_belt_radial_load(
    *,
    effective_tension_difference_n: float,
    installation_tension_per_span_n: float,
    span_included_angle_rad: float,
) -> BeltRadialLoad:
    """Resolve the two belt-span forces acting on one pulley."""

    _nonnegative_finite(
        "effective_tension_difference_n", effective_tension_difference_n
    )
    _positive_finite("installation_tension_per_span_n", installation_tension_per_span_n)
    if (
        not math.isfinite(span_included_angle_rad)
        or span_included_angle_rad < 0.0
        or span_included_angle_rad >= math.pi
    ):
        raise ValueError("span_included_angle_rad must be finite in [0, pi)")
    tight = installation_tension_per_span_n + effective_tension_difference_n
    slack = installation_tension_per_span_n
    resultant = math.sqrt(
        tight**2
        + slack**2
        + 2.0 * tight * slack * math.cos(span_included_angle_rad)
    )
    return BeltRadialLoad(
        effective_tension_difference_n=effective_tension_difference_n,
        installation_tension_per_span_n=installation_tension_per_span_n,
        span_included_angle_rad=span_included_angle_rad,
        tight_span_tension_n=tight,
        slack_span_tension_n=slack,
        resultant_radial_load_n=resultant,
    )


def screen_supported_input_shaft(
    *, radial_load_n: float, design_torque_nm: float
) -> SupportedShaftScreen:
    """Screen the selected 8 mm shaft between two 608 bearings."""

    _positive_finite("radial_load_n", radial_load_n)
    _positive_finite("design_torque_nm", design_torque_nm)
    diameter = SUPPORTED_INPUT_SHAFT_DIAMETER_M
    maximum_bending_moment = radial_load_n * INPUT_BEARING_SPAN_M / 4.0
    bending = 32.0 * maximum_bending_moment / (math.pi * diameter**3)
    torsion = 16.0 * design_torque_nm / (math.pi * diameter**3)
    von_mises = KEYWAY_FATIGUE_STRESS_MULTIPLIER * math.sqrt(
        bending**2 + 3.0 * torsion**2
    )
    reaction = radial_load_n / 2.0
    return SupportedShaftScreen(
        shaft_diameter_m=diameter,
        bearing_span_m=INPUT_BEARING_SPAN_M,
        radial_load_n=radial_load_n,
        reaction_per_bearing_n=reaction,
        maximum_bending_moment_nm=maximum_bending_moment,
        design_torque_nm=design_torque_nm,
        nominal_bending_stress_pa=bending,
        nominal_torsional_shear_pa=torsion,
        factored_von_mises_stress_pa=von_mises,
        provisional_yield_strength_pa=PROVISIONAL_C45_YIELD_STRENGTH_PA,
        yield_safety_factor=PROVISIONAL_C45_YIELD_STRENGTH_PA / von_mises,
        bearing_dynamic_rating_n=SKF_608_DYNAMIC_RATING_N,
        bearing_rating_utilization=reaction / SKF_608_DYNAMIC_RATING_N,
        coupling_rated_torque_nm=BKL3_RATED_TORQUE_NM,
        coupling_torque_factor=BKL3_RATED_TORQUE_NM / design_torque_nm,
    )


def budget_mechanical_closure_document() -> dict[str, object]:
    """Return deterministic mechanical evidence for the selected 20/60 drive."""

    candidate = BUDGET_TRANSMISSION_CANDIDATES[0]
    geometry = solve_open_belt_geometry(candidate.belt)
    performance = assess_budget_operating_point(
        candidate, payload_kg=0.50, cycle_duration_s=1.50
    )
    direct_rejected = (
        performance.peak_belt_tension_difference_n > MOTOR_DYNAMIC_RADIAL_LIMIT_N
    )
    load = calculate_belt_radial_load(
        effective_tension_difference_n=(
            DESIGN_FACTOR * performance.peak_belt_tension_difference_n
        ),
        installation_tension_per_span_n=GATES_5M_15_MIN_INSTALLATION_TENSION_N,
        span_included_angle_rad=math.pi - geometry.small_wrap_angle_rad,
    )
    shaft = screen_supported_input_shaft(
        radial_load_n=load.resultant_radial_load_n,
        design_torque_nm=performance.required_peak_torque_nm,
    )
    transmission = budget_transmission(candidate)
    accepted = (
        direct_rejected
        and performance.status == "not_rejected_by_proxy"
        and shaft.yield_safety_factor >= 2.0
        and shaft.bearing_rating_utilization < 0.10
        and shaft.coupling_torque_factor >= 1.30
    )
    return {
        "schema": "delta-robot-budget-mechanical-closure/v1",
        "status": "digital_screen_passed_physical_p1_pending" if accepted else "rejected",
        "transmission_id": candidate.candidate_id,
        "geometry": asdict(geometry),
        "performance_point": asdict(performance),
        "direct_motor_shaft": {
            "status": "rejected" if direct_rejected else "not_rejected",
            "motor_dynamic_radial_limit_n": MOTOR_DYNAMIC_RADIAL_LIMIT_N,
            "peak_effective_tension_difference_n": (
                performance.peak_belt_tension_difference_n
            ),
            "reason": "effective tension alone exceeds motor limit before installation tension"
            if direct_rejected
            else "requires preload-inclusive manufacturer confirmation",
        },
        "supported_input": {
            "arrangement": (
                "20T pulley centred between two 608 bearings; motor connected by "
                "BKL/3/8/8"
            ),
            "belt_load": asdict(load),
            "shaft_screen": asdict(shaft),
            "input_shaft_model_length_m": SUPPORTED_INPUT_SHAFT_LENGTH_M,
            "input_shaft_inertia_kg_m2": transmission.inertia.input_shaft_kg_m2,
            "coupling_mass_kg": BKL3_COUPLING_MASS_KG,
            "coupling_outer_diameter_m": BKL3_COUPLING_OUTER_DIAMETER_M,
            "coupling_inertia_upper_bound_kg_m2": transmission.inertia.coupling_kg_m2,
        },
        "sources": {
            "belt_installation_tension": (
                "Gates PowerGrip GT3 Design Manual, 5M HTD, 15 mm, "
                "Min Tst 13.5 lbf"
            ),
            "bearing": "SKF 608-2RSH envelope, C=3.32 kN",
            "coupling": "R+W BKL size 3, rated torque 3 Nm",
        },
        "remaining_blockers": [
            "measure delivered pulley, shaft, bearing and coupling dimensions before "
            "fabrication release",
            "freeze fits, keyway and axial retention after delivered-part measurement",
            "set and measure belt installation tension on the physical bench",
            "run physical P1 temperature, following-error and bus-voltage tests",
        ],
    }
