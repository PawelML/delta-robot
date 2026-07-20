"""Reproducible report adapter for simplified P1 dynamics."""

from dataclasses import asdict

from delta_model.design_geometry import SELECTED_SOURCE_LABEL
from delta_model.drive_sizing import (
    LEADSHINE_ISV2_RS6040V48G,
    assess_motor_candidate,
)
from delta_model.dynamics import (
    CONSERVATIVE_MASS_CASE,
    DESIGN_FACTOR,
    NOMINAL_MASS_CASE,
    STANDARD_GRAVITY_M_S2,
    TRANSMISSION_EFFICIENCY,
    DynamicCaseResult,
    evaluate_dynamic_case,
    transmission_requirement,
)
from delta_model.trajectory import generate_trajectory


def _case_document(result: DynamicCaseResult) -> dict[str, object]:
    return {
        "axes": [asdict(axis) for axis in result.axes],
        "mass_case": asdict(result.mass_case),
        "sample_count": len(result.times_s),
    }


def _maximum_relative_change(coarse: DynamicCaseResult, fine: DynamicCaseResult) -> float:
    changes: list[float] = []
    for coarse_axis, fine_axis in zip(coarse.axes, fine.axes, strict=True):
        for coarse_value, fine_value in (
            (coarse_axis.peak_abs_torque_nm, fine_axis.peak_abs_torque_nm),
            (coarse_axis.rms_torque_nm, fine_axis.rms_torque_nm),
        ):
            changes.append(abs(coarse_value - fine_value) / max(abs(fine_value), 1e-15))
    return max(changes)


def dynamic_sizing_document() -> dict[str, object]:
    """Evaluate two mass cases, convergence and two belt reductions."""

    trajectory = generate_trajectory()
    fine_trajectory = generate_trajectory(sample_period_s=0.0005)
    nominal = evaluate_dynamic_case(trajectory, NOMINAL_MASS_CASE)
    conservative = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    fine_nominal = evaluate_dynamic_case(fine_trajectory, NOMINAL_MASS_CASE)
    fine_conservative = evaluate_dynamic_case(fine_trajectory, CONSERVATIVE_MASS_CASE)
    convergence = max(
        _maximum_relative_change(nominal, fine_nominal),
        _maximum_relative_change(conservative, fine_conservative),
    )
    requirements = tuple(
        transmission_requirement(conservative, ratio=ratio) for ratio in (3.0, 5.0)
    )
    candidate_assessment = assess_motor_candidate(
        trajectory,
        conservative,
        LEADSHINE_ISV2_RS6040V48G,
    )
    return {
        "cases": [_case_document(nominal), _case_document(conservative)],
        "candidate_assessment": {
            "axes": [asdict(axis) for axis in candidate_assessment.axes],
            "candidate": asdict(candidate_assessment.candidate),
            "design_factor": candidate_assessment.design_factor,
            "efficiency": candidate_assessment.efficiency,
            "maximum_motor_acceleration_rad_s2": (
                candidate_assessment.maximum_motor_acceleration_rad_s2
            ),
            "maximum_motor_speed_rpm": candidate_assessment.maximum_motor_speed_rpm,
            "passes": candidate_assessment.passes,
            "ratio": candidate_assessment.ratio,
        },
        "convergence": {
            "fine_sample_period_s": fine_trajectory.sample_period_s,
            "maximum_relative_peak_or_rms_change": convergence,
            "passes_one_percent": convergence < 0.01,
        },
        "limitations": [
            "all component masses are provisional and must be weighed",
            "lower-arm assemblies are split equally between platform and knees",
            "friction, compliance, belt and hose forces are excluded",
            "generic transmission rows exclude motor and pulley inertia",
            "candidate assessment includes motor rotor inertia but excludes pulley inertia",
            "torque-speed and thermal feasibility require manufacturer data and a bench test",
        ],
        "model": {
            "design_factor": DESIGN_FACTOR,
            "gravity_m_s2": STANDARD_GRAVITY_M_S2,
            "lower_mass_model": "half_translating_half_equally_knee_lumped",
            "transmission_efficiency": TRANSMISSION_EFFICIENCY,
            "upper_arm_model": "uniform_rigid_link",
        },
        "schema": "delta-robot-p1-dynamic-sizing/v1",
        "source": SELECTED_SOURCE_LABEL,
        "status": "provisional_pass" if convergence < 0.01 else "sampling_not_converged",
        "trajectory": {
            "duration_s": trajectory.duration_s,
            "name": "25-305-25_round_trip_1_hz",
            "sample_count": len(trajectory.samples),
            "sample_period_s": trajectory.sample_period_s,
        },
        "transmissions": [asdict(requirement) for requirement in requirements],
        "units": {
            "angle": "rad",
            "angular_acceleration": "rad/s^2",
            "angular_velocity": "rad/s",
            "mass": "kg",
            "torque": "N*m",
        },
        "warnings": [
            "one representative drive only before the P1 bench gate",
            "selection does not authorize a three-drive purchase",
        ],
    }
