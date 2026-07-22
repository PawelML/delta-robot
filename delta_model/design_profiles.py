"""Named hardware profiles sharing the authoritative delta model."""

from dataclasses import asdict, dataclass
from typing import Literal

from delta_model.drive_sizing import (
    INDUSTRIAL_REFERENCE_TRANSMISSION,
    LEADSHINE_ISV2_RS6040V48G,
    ClosedLoopStepperCandidate,
    DriveTransmission,
    MotorCandidate,
    TorqueSpeedCurve,
    TorqueSpeedPoint,
)

ProfileId = Literal["industrial_reference", "budget_demonstrator"]


@dataclass(frozen=True, slots=True)
class IndustrialReferenceProfile:
    """Calculated Leadshine/Gates reference retained for regression and upgrade."""

    profile_id: Literal["industrial_reference"]
    role: Literal["reference_not_active_purchase"]
    motor: MotorCandidate
    transmission: DriveTransmission
    evidence_status: Literal["calculated_physical_p1_pending"]


@dataclass(frozen=True, slots=True)
class BudgetDemonstratorProfile:
    """Budget drive candidate with intentionally incomplete transmission data."""

    profile_id: Literal["budget_demonstrator"]
    role: Literal["active_development"]
    motor: ClosedLoopStepperCandidate
    transmission: None
    evidence_status: Literal["candidate_curve_proxy_transmission_pending"]
    total_budget_min_pln_gross: int
    total_budget_max_pln_gross: int
    delivery_country: str


DesignProfile = IndustrialReferenceProfile | BudgetDemonstratorProfile


STEPPERONLINE_23HS40_PROXY_CURVE = TorqueSpeedCurve(
    points=(
        TorqueSpeedPoint(100.0, 2.30),
        TorqueSpeedPoint(200.0, 2.25),
        TorqueSpeedPoint(300.0, 2.00),
        TorqueSpeedPoint(400.0, 1.70),
        TorqueSpeedPoint(500.0, 1.60),
        TorqueSpeedPoint(600.0, 1.35),
        TorqueSpeedPoint(700.0, 1.12),
        TorqueSpeedPoint(800.0, 1.03),
        TorqueSpeedPoint(900.0, 0.95),
        TorqueSpeedPoint(1000.0, 0.80),
        TorqueSpeedPoint(1100.0, 0.78),
        TorqueSpeedPoint(1200.0, 0.77),
        TorqueSpeedPoint(1300.0, 0.70),
        TorqueSpeedPoint(1400.0, 0.68),
        TorqueSpeedPoint(1500.0, 0.62),
    ),
    evidence_status="proxy_only",
    test_conditions="CL57T-V41, 36 VDC, 5.0 A RMS, 2000 microsteps/rev",
    source_url=(
        "https://www.stepperonline.ca/image/catalog/torque-curves/"
        "23HS40-5004D-E1000_Torque_Curve.svg"
    ),
    digitization_uncertainty_nm=0.03,
)


STEPPERONLINE_3_CLYS30_V20 = ClosedLoopStepperCandidate(
    kit_model="StepperOnline 3-CLYS30-V20",
    motor_model="23HS40-5004D-E1000",
    driver_model="CL57Y-V20",
    supply_model="S-500-48",
    holding_torque_nm=3.00,
    rotor_inertia_kg_m2=660.0e-7,
    motor_mass_kg=1.65,
    rated_phase_current_a=5.0,
    phase_resistance_ohm=0.6,
    phase_inductance_mh=2.3,
    step_angle_deg=1.8,
    encoder_ppr=1000,
    encoder_cpr=4000,
    shaft_diameter_m=0.008,
    supply_voltage_vdc=48.0,
    supply_power_w=500.0,
    supply_current_a=10.5,
    driver_voltage_min_vdc=24.0,
    driver_voltage_max_vdc=50.0,
    driver_peak_current_a=7.0,
    torque_speed_curve=STEPPERONLINE_23HS40_PROXY_CURVE,
    kit_source_url=(
        "https://www.stepperonline.com.tr/ys-serisi-3-eksenli-kapali-dongu-"
        "adimlayici-cnc-kiti-v2-0-3-00-nm-424-83-oz-in-nema-23-motor-2-0-m-"
        "kablolar-ve-guc-kaynagi-ile-3-clys30-v20"
    ),
    motor_source_url=(
        "https://www.stepperonline.ca/s-series-nema-23-closed-loop-stepper-motor-"
        "3-00nm-424-83oz-in-encoder-1000ppr-4000cpr-23hs40-5004d-e1000.html"
    ),
)


INDUSTRIAL_REFERENCE_PROFILE = IndustrialReferenceProfile(
    profile_id="industrial_reference",
    role="reference_not_active_purchase",
    motor=LEADSHINE_ISV2_RS6040V48G,
    transmission=INDUSTRIAL_REFERENCE_TRANSMISSION,
    evidence_status="calculated_physical_p1_pending",
)


BUDGET_DEMONSTRATOR_PROFILE = BudgetDemonstratorProfile(
    profile_id="budget_demonstrator",
    role="active_development",
    motor=STEPPERONLINE_3_CLYS30_V20,
    transmission=None,
    evidence_status="candidate_curve_proxy_transmission_pending",
    total_budget_min_pln_gross=5000,
    total_budget_max_pln_gross=6000,
    delivery_country="Poland",
)


PROFILES: tuple[DesignProfile, ...] = (
    INDUSTRIAL_REFERENCE_PROFILE,
    BUDGET_DEMONSTRATOR_PROFILE,
)


def get_design_profile(profile_id: str) -> DesignProfile:
    """Return a stable named profile or reject an unknown identifier."""

    for profile in PROFILES:
        if profile.profile_id == profile_id:
            return profile
    raise ValueError(f"unknown design profile: {profile_id}")


def require_selected_transmission(profile: DesignProfile) -> DriveTransmission:
    """Return a complete transmission or stop an invalid profile calculation."""

    if profile.transmission is None:
        raise ValueError(f"profile {profile.profile_id} has no selected transmission")
    return profile.transmission


def design_profiles_document() -> dict[str, object]:
    """Return deterministic human- and machine-readable profile evidence."""

    return {
        "profiles": [asdict(profile) for profile in PROFILES],
        "schema": "delta-robot-design-profiles/v1",
        "shared_model": {
            "geometry": "selected_180_65_280_450_mm",
            "mathematical_source": "delta_model Python package",
            "workspace": "diameter_400_mm_x_z_150_mm",
        },
        "warnings": [
            "industrial_reference is retained but is not the active purchase plan",
            "budget transmission, payload and cycle time are not selected",
            "budget torque-speed curve uses the exact motor but a different driver and 36 V",
            "holding torque is not available running torque",
        ],
    }
