"""Catalogue-backed geometry and screening calculations for the P1 belt drive."""

import math
from dataclasses import asdict, dataclass
from typing import Literal

BELT_PITCH_M = 0.005
SELECTED_RATIO = 5.0
POUND_FORCE_TO_NEWTON = 4.4482216152605
POUND_FOOT_SQUARED_TO_KG_M2 = 0.0421401101
HORSEPOWER_TO_WATT = 745.6998715822702


@dataclass(frozen=True, slots=True)
class BeltCandidate:
    """Exact-ratio geometric candidate and catalogue-status inputs."""

    candidate_id: str
    small_teeth: int
    large_teeth: int
    belt_pitch_length_m: float
    belt_width_m: float
    small_pulley_catalogue: str | None
    large_pulley_catalogue: str | None
    published_rating_available: bool
    published_stock_pair: bool

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be empty")
        if self.small_teeth <= 0 or self.large_teeth <= 0:
            raise ValueError("pulley tooth counts must be positive")
        if self.large_teeth <= self.small_teeth:
            raise ValueError("large pulley must have more teeth than small pulley")
        if not math.isfinite(self.belt_pitch_length_m) or self.belt_pitch_length_m <= 0.0:
            raise ValueError("belt pitch length must be finite and positive")
        if not math.isfinite(self.belt_width_m) or self.belt_width_m <= 0.0:
            raise ValueError("belt width must be finite and positive")

    @property
    def ratio(self) -> float:
        return self.large_teeth / self.small_teeth


@dataclass(frozen=True, slots=True)
class BeltGeometry:
    """Solved open-belt geometry in SI units."""

    small_pitch_diameter_m: float
    large_pitch_diameter_m: float
    centre_distance_m: float
    reconstructed_pitch_length_m: float
    small_wrap_angle_rad: float
    small_wrap_angle_deg: float
    small_teeth_in_mesh: float


@dataclass(frozen=True, slots=True)
class ShaftScreen:
    """Simple centred-load shaft screen; keyway and fatigue effects are excluded."""

    diameter_m: float
    bearing_span_m: float
    radial_load_upper_bound_n: float
    bearing_reaction_each_n: float
    maximum_bending_moment_nm: float
    transmitted_torque_nm: float
    bending_stress_mpa: float
    torsional_stress_mpa: float
    von_mises_stress_mpa: float


@dataclass(frozen=True, slots=True)
class CandidateScreen:
    """Geometry and deterministic recommendation status for one candidate."""

    candidate: BeltCandidate
    geometry: BeltGeometry
    status: Literal["recommended", "rejected"]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Selected-drive operating calculations."""

    maximum_motor_speed_rpm: float
    belt_speed_m_s: float
    peak_design_transmitted_torque_nm: float
    pitch_line_tension_difference_n: float
    installation_tension_each_span_n: float
    conservative_radial_load_n: float
    maximum_trajectory_belt_power_w: float
    belt_power_service_factor: float
    design_belt_power_w: float
    interpolated_catalogue_capacity_w: float
    capacity_utilization: float
    capacity_status: Literal["passes", "fails", "not_evaluated"]


VARIANTS = (
    BeltCandidate(
        candidate_id="16_80_535",
        small_teeth=16,
        large_teeth=80,
        belt_pitch_length_m=0.535,
        belt_width_m=0.015,
        small_pulley_catalogue=None,
        large_pulley_catalogue=None,
        published_rating_available=False,
        published_stock_pair=False,
    ),
    BeltCandidate(
        candidate_id="18_90_600",
        small_teeth=18,
        large_teeth=90,
        belt_pitch_length_m=0.600,
        belt_width_m=0.015,
        small_pulley_catalogue="Gates P18-5MGT-15AL",
        large_pulley_catalogue="Gates P90-5MGT-15 with 1610-20 mm bushing",
        published_rating_available=True,
        published_stock_pair=True,
    ),
    BeltCandidate(
        candidate_id="20_100_625",
        small_teeth=20,
        large_teeth=100,
        belt_pitch_length_m=0.625,
        belt_width_m=0.015,
        small_pulley_catalogue=None,
        large_pulley_catalogue=None,
        published_rating_available=False,
        published_stock_pair=False,
    ),
)


def pitch_diameter_m(teeth: int, pitch_m: float = BELT_PITCH_M) -> float:
    """Return synchronous-pulley pitch diameter."""

    if teeth <= 0 or not math.isfinite(pitch_m) or pitch_m <= 0.0:
        raise ValueError("teeth and pitch must be positive")
    return teeth * pitch_m / math.pi


def open_belt_length_m(
    centre_distance_m: float,
    small_diameter_m: float,
    large_diameter_m: float,
) -> float:
    """Return the standard open-belt pitch-length approximation."""

    values = (centre_distance_m, small_diameter_m, large_diameter_m)
    if not all(math.isfinite(value) and value > 0.0 for value in values):
        raise ValueError("belt dimensions must be finite and positive")
    if large_diameter_m <= small_diameter_m:
        raise ValueError("large diameter must exceed small diameter")
    return (
        2.0 * centre_distance_m
        + math.pi * (large_diameter_m + small_diameter_m) / 2.0
        + (large_diameter_m - small_diameter_m) ** 2 / (4.0 * centre_distance_m)
    )


def solve_open_belt_geometry(candidate: BeltCandidate) -> BeltGeometry:
    """Solve centre distance and wrap from tooth counts and belt pitch length."""

    small = pitch_diameter_m(candidate.small_teeth)
    large = pitch_diameter_m(candidate.large_teeth)
    residual = candidate.belt_pitch_length_m - math.pi * (large + small) / 2.0
    discriminant = residual**2 - 2.0 * (large - small) ** 2
    if discriminant <= 0.0:
        raise ValueError("belt is too short for a physical open-drive solution")
    centre = (residual + math.sqrt(discriminant)) / 4.0
    if centre <= (large - small) / 2.0:
        raise ValueError("solved centre distance does not produce an open belt")
    wrap = math.pi - 2.0 * math.asin((large - small) / (2.0 * centre))
    reconstructed = open_belt_length_m(centre, small, large)
    return BeltGeometry(
        small_pitch_diameter_m=small,
        large_pitch_diameter_m=large,
        centre_distance_m=centre,
        reconstructed_pitch_length_m=reconstructed,
        small_wrap_angle_rad=wrap,
        small_wrap_angle_deg=math.degrees(wrap),
        small_teeth_in_mesh=candidate.small_teeth * wrap / (2.0 * math.pi),
    )


def screen_candidate(candidate: BeltCandidate) -> CandidateScreen:
    """Apply catalogue, ratio and minimum-mesh requirements."""

    geometry = solve_open_belt_geometry(candidate)
    reasons: list[str] = []
    if not math.isclose(candidate.ratio, SELECTED_RATIO, rel_tol=0.0, abs_tol=1e-12):
        reasons.append("ratio_is_not_exactly_5_to_1")
    if geometry.small_teeth_in_mesh < 6.0:
        reasons.append("fewer_than_six_small_pulley_teeth_in_mesh")
    if not candidate.published_rating_available:
        reasons.append("no_applicable_published_power_rating")
    if not candidate.published_stock_pair:
        reasons.append("published_stock_pulley_pair_not_confirmed")
    selected = candidate.candidate_id == "18_90_600" and not reasons
    return CandidateScreen(
        candidate=candidate,
        geometry=geometry,
        status="recommended" if selected else "rejected",
        reasons=tuple(reasons),
    )


def interpolate_selected_belt_capacity_w(motor_speed_rpm: float) -> float:
    """Interpolate Gates 18T/15 mm data only over its published 300-400 rpm range."""

    if not math.isfinite(motor_speed_rpm) or not 300.0 <= motor_speed_rpm <= 400.0:
        raise ValueError("published interpolation is limited to 300..400 rpm")
    power_hp = 0.32 + (motor_speed_rpm - 300.0) * (0.40 - 0.32) / 100.0
    return power_hp * HORSEPOWER_TO_WATT * 0.95


def selected_operating_point(
    *,
    maximum_motor_speed_rpm: float,
    peak_design_transmitted_torque_nm: float,
    maximum_trajectory_belt_power_w: float,
    belt_power_service_factor: float = 1.50,
    installation_tension_factor: float = 1.50,
) -> OperatingPoint:
    """Calculate speed, pitch-line force and catalogue power screen."""

    values = (
        maximum_motor_speed_rpm,
        peak_design_transmitted_torque_nm,
        maximum_trajectory_belt_power_w,
        belt_power_service_factor,
        installation_tension_factor,
    )
    if not all(math.isfinite(value) and value > 0.0 for value in values):
        raise ValueError("operating-point inputs must be finite and positive")
    selected = VARIANTS[1]
    radius = pitch_diameter_m(selected.small_teeth) / 2.0
    omega = maximum_motor_speed_rpm * 2.0 * math.pi / 60.0
    belt_speed = omega * radius
    tension_difference = peak_design_transmitted_torque_nm / radius
    installation_tension = 15.0 * POUND_FORCE_TO_NEWTON * installation_tension_factor
    radial_load = 2.0 * installation_tension + tension_difference
    design_power = maximum_trajectory_belt_power_w * belt_power_service_factor
    try:
        capacity = interpolate_selected_belt_capacity_w(maximum_motor_speed_rpm)
    except ValueError:
        capacity = math.nan
        capacity_status: Literal["passes", "fails", "not_evaluated"] = "not_evaluated"
        utilization = math.nan
    else:
        utilization = design_power / capacity
        capacity_status = "passes" if utilization <= 1.0 else "fails"
    return OperatingPoint(
        maximum_motor_speed_rpm=maximum_motor_speed_rpm,
        belt_speed_m_s=belt_speed,
        peak_design_transmitted_torque_nm=peak_design_transmitted_torque_nm,
        pitch_line_tension_difference_n=tension_difference,
        installation_tension_each_span_n=installation_tension,
        conservative_radial_load_n=radial_load,
        maximum_trajectory_belt_power_w=maximum_trajectory_belt_power_w,
        belt_power_service_factor=belt_power_service_factor,
        design_belt_power_w=design_power,
        interpolated_catalogue_capacity_w=capacity,
        capacity_utilization=utilization,
        capacity_status=capacity_status,
    )


def shaft_screen(
    *,
    diameter_m: float,
    bearing_span_m: float,
    radial_load_n: float,
    transmitted_torque_nm: float,
) -> ShaftScreen:
    """Screen a simply-supported solid circular shaft with a centred pulley load."""

    values = (diameter_m, bearing_span_m, radial_load_n, transmitted_torque_nm)
    if not all(math.isfinite(value) and value > 0.0 for value in values):
        raise ValueError("shaft screen inputs must be finite and positive")
    moment = radial_load_n * bearing_span_m / 4.0
    bending = 32.0 * moment / (math.pi * diameter_m**3)
    torsion = 16.0 * transmitted_torque_nm / (math.pi * diameter_m**3)
    von_mises = math.sqrt(bending**2 + 3.0 * torsion**2)
    return ShaftScreen(
        diameter_m=diameter_m,
        bearing_span_m=bearing_span_m,
        radial_load_upper_bound_n=radial_load_n,
        bearing_reaction_each_n=radial_load_n / 2.0,
        maximum_bending_moment_nm=moment,
        transmitted_torque_nm=transmitted_torque_nm,
        bending_stress_mpa=bending / 1e6,
        torsional_stress_mpa=torsion / 1e6,
        von_mises_stress_mpa=von_mises / 1e6,
    )


def inertia_from_wr2_lb_ft2(wr2_lb_ft2: float) -> float:
    """Convert catalogue WR² to SI mass moment of inertia."""

    if not math.isfinite(wr2_lb_ft2) or wr2_lb_ft2 < 0.0:
        raise ValueError("WR² must be finite and non-negative")
    return wr2_lb_ft2 * POUND_FOOT_SQUARED_TO_KG_M2


def transmission_document(
    *,
    maximum_motor_speed_rpm: float,
    peak_design_transmitted_torque_nm: float,
    maximum_trajectory_belt_power_w: float,
) -> dict[str, object]:
    """Build the deterministic transmission-selection report."""

    screens = tuple(screen_candidate(candidate) for candidate in VARIANTS)
    operating = selected_operating_point(
        maximum_motor_speed_rpm=maximum_motor_speed_rpm,
        peak_design_transmitted_torque_nm=peak_design_transmitted_torque_nm,
        maximum_trajectory_belt_power_w=maximum_trajectory_belt_power_w,
    )
    input_shaft = shaft_screen(
        diameter_m=0.009525,
        bearing_span_m=0.050,
        radial_load_n=operating.conservative_radial_load_n,
        transmitted_torque_nm=peak_design_transmitted_torque_nm,
    )
    output_shaft = shaft_screen(
        diameter_m=0.020,
        bearing_span_m=0.070,
        radial_load_n=operating.conservative_radial_load_n,
        transmitted_torque_nm=peak_design_transmitted_torque_nm * 5.0 * 0.90,
    )
    return {
        "candidates": [
            {
                "candidate": asdict(screen.candidate),
                "geometry": asdict(screen.geometry),
                "reasons": list(screen.reasons),
                "status": screen.status,
            }
            for screen in screens
        ],
        "inertias": {
            "belt_estimated_kg": 0.01715,
            "large_pulley_kg_m2": inertia_from_wr2_lb_ft2(0.1358),
            "small_pulley_kg_m2": inertia_from_wr2_lb_ft2(0.000097),
            "source_note": (
                "pulley WR2 from Gates catalogue; belt mass scales the official "
                "1000 mm product mass linearly and remains an estimate"
            ),
        },
        "operating_point": asdict(operating),
        "recommendation": {
            "adjustment_travel_m": 0.025,
            "belt": "Gates 600-5MGT-15",
            "large_pulley": "Gates P90-5MGT-15 with 1610-20 mm bushing",
            "ratio": 5.0,
            "small_pulley": "Gates P18-5MGT-15AL on supported 3/8 inch jackshaft",
            "status": "provisional_for_p1_bench",
        },
        "schema": "delta-robot-p1-transmission-selection/v1",
        "shaft_screens": {
            "input_jackshaft": asdict(input_shaft),
            "output_shaft": asdict(output_shaft),
        },
        "sources": {
            "gates_gt3_manual": (
                "https://www.gates.com/content/dam/documents-library/catalogs/"
                "powergrip-gt3-drive-design-manual-en.pdf"
            ),
            "gates_precision_manual": (
                "https://www.gates.com/content/dam/gates/home/knowledge-center/"
                "resource-library/catalogs/light-power-and-precision-manual.pdf"
            ),
            "leadshine_manual": (
                "https://www.leadshine.com/upfiles/downloads/"
                "f85ab001e8edd4c7f05e5c32ea6671fd_1766721032370.pdf"
            ),
        },
        "unverified": [
            "actual belt tension and alignment",
            "supplier stock and finished bores",
            "keyway and fatigue stress concentrations",
            "bearing fits, runout, vibration and compliance",
        ],
    }
