import json
from pathlib import Path

import pytest

from delta_model.design_profiles import (
    BUDGET_DEMONSTRATOR_PROFILE,
    INDUSTRIAL_REFERENCE_PROFILE,
    STEPPERONLINE_23HS40_PROXY_CURVE,
    design_profiles_document,
    get_design_profile,
    require_selected_transmission,
)
from delta_model.drive_sizing import TorqueSpeedCurve, TorqueSpeedPoint
from delta_model.transmission import pitch_diameter_m


def test_named_profiles_are_explicit_and_distinct() -> None:
    industrial = get_design_profile("industrial_reference")
    budget = get_design_profile("budget_demonstrator")

    assert industrial is INDUSTRIAL_REFERENCE_PROFILE
    assert budget is BUDGET_DEMONSTRATOR_PROFILE
    assert industrial.role == "reference_not_active_purchase"
    assert budget.role == "active_development"
    assert budget.transmission is None
    assert budget.provisional_transmission_id == "catalogue_20_60_450"
    assert budget.provisional_payload_kg == pytest.approx(0.50)
    assert budget.provisional_cycle_duration_s == pytest.approx(1.50)
    assert budget.total_budget_max_pln_gross == 6000


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown design profile"):
        get_design_profile("silent-third-profile")


def test_incomplete_budget_transmission_is_rejected_explicitly() -> None:
    with pytest.raises(ValueError, match="has no selected transmission"):
        require_selected_transmission(BUDGET_DEMONSTRATOR_PROFILE)

    assert (
        require_selected_transmission(INDUSTRIAL_REFERENCE_PROFILE)
        is INDUSTRIAL_REFERENCE_PROFILE.transmission
    )


def test_industrial_profile_preserves_selected_transmission() -> None:
    transmission = INDUSTRIAL_REFERENCE_PROFILE.transmission

    assert transmission.ratio == pytest.approx(5.0)
    assert transmission.efficiency == pytest.approx(0.90)
    assert transmission.small_pulley_pitch_radius_m == pytest.approx(
        pitch_diameter_m(18) / 2.0
    )


def test_budget_profile_identifies_exact_kit_components() -> None:
    motor = BUDGET_DEMONSTRATOR_PROFILE.motor

    assert motor.kit_model == "StepperOnline 3-CLYS30-V20"
    assert motor.motor_model == "23HS40-5004D-E1000"
    assert motor.driver_model == "CL57Y-V20"
    assert motor.supply_model == "S-500-48"
    assert motor.rotor_inertia_kg_m2 == pytest.approx(6.60e-5)
    assert motor.torque_speed_curve.evidence_status == "proxy_only"


def test_proxy_curve_interpolates_only_inside_published_interval() -> None:
    curve = STEPPERONLINE_23HS40_PROXY_CURVE

    assert curve.available_torque_nm(300.0) == pytest.approx(2.00)
    assert curve.available_torque_nm(350.0) == pytest.approx(1.85)
    assert curve.available_torque_nm(1500.0) == pytest.approx(0.62)
    with pytest.raises(ValueError, match="outside published curve"):
        curve.available_torque_nm(99.9)
    with pytest.raises(ValueError, match="outside published curve"):
        curve.available_torque_nm(1500.1)


def test_curve_rejects_duplicate_speeds() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        TorqueSpeedCurve(
            points=(TorqueSpeedPoint(100.0, 2.0), TorqueSpeedPoint(100.0, 1.9)),
            evidence_status="proxy_only",
            test_conditions="test",
            source_url="https://example.test/curve",
            digitization_uncertainty_nm=0.01,
        )


def test_design_profile_document_matches_committed_artifact() -> None:
    artifact = Path(__file__).resolve().parents[1] / "artifacts/design_profiles.json"
    committed = json.loads(artifact.read_text(encoding="utf-8"))

    assert json.loads(json.dumps(design_profiles_document())) == committed
    assert committed["schema"] == "delta-robot-design-profiles/v1"
