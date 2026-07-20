"""Reproducible report and trace adapters for P1 dynamics."""

import csv
import io
from dataclasses import asdict

from delta_model.design_geometry import SELECTED_SOURCE_LABEL
from delta_model.drive_sizing import (
    LEADSHINE_ISV2_RS6040V48G,
    P1_TRANSMISSION_INERTIA,
    RefinedDriveAssessment,
    assess_motor_candidate,
    assess_refined_drive,
)
from delta_model.dynamics import (
    CONSERVATIVE_MASS_CASE,
    DESIGN_FACTOR,
    NOMINAL_MASS_CASE,
    STANDARD_GRAVITY_M_S2,
    TRANSMISSION_EFFICIENCY,
    DynamicCaseResult,
    DynamicMassCase,
    evaluate_dynamic_case,
    joint_effective_inertias_kg_m2,
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


def _refined_document(result: RefinedDriveAssessment) -> dict[str, object]:
    return {
        "axes": [asdict(axis) for axis in result.axes],
        "design_factor": result.design_factor,
        "efficiency": result.efficiency,
        "maximum_belt_power_w": result.maximum_belt_power_w,
        "maximum_motor_acceleration_rad_s2": result.maximum_motor_acceleration_rad_s2,
        "maximum_motor_speed_rpm": result.maximum_motor_speed_rpm,
        "passes": result.passes,
        "ratio": result.ratio,
        "time_history": "artifacts/p1_refined_drive_trace.csv",
    }


def refined_drive_trace_csv() -> str:
    """Return the selected conservative drive's deterministic sample trace."""

    trajectory = generate_trajectory()
    dynamic = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    assessment = assess_refined_drive(
        trajectory,
        dynamic,
        LEADSHINE_ISV2_RS6040V48G,
    )
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "time_s",
            "motor_torque_axis_1_nm",
            "motor_torque_axis_2_nm",
            "motor_torque_axis_3_nm",
            "belt_torque_axis_1_nm",
            "belt_torque_axis_2_nm",
            "belt_torque_axis_3_nm",
        )
    )
    for time_s, motor_row, belt_row in zip(
        dynamic.times_s,
        assessment.motor_torques_nm,
        assessment.belt_torques_nm,
        strict=True,
    ):
        writer.writerow((time_s, *motor_row, *belt_row))
    return output.getvalue()


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
    legacy_candidate_assessment = assess_motor_candidate(
        trajectory,
        conservative,
        LEADSHINE_ISV2_RS6040V48G,
    )
    candidate_assessment = assess_refined_drive(
        trajectory,
        conservative,
        LEADSHINE_ISV2_RS6040V48G,
    )
    arm_mass_variants = []
    for upper_arm_mass_kg in (0.15, 0.20, 0.25, 0.30):
        mass_case = DynamicMassCase(
            case_id=f"conservative_with_{upper_arm_mass_kg:.2f}kg_upper_arm",
            payload_kg=CONSERVATIVE_MASS_CASE.payload_kg,
            platform_tooling_kg=CONSERVATIVE_MASS_CASE.platform_tooling_kg,
            upper_arm_each_kg=upper_arm_mass_kg,
            lower_assemblies_total_kg=CONSERVATIVE_MASS_CASE.lower_assemblies_total_kg,
        )
        variant_dynamic = evaluate_dynamic_case(trajectory, mass_case)
        variant_drive = assess_refined_drive(
            trajectory,
            variant_dynamic,
            LEADSHINE_ISV2_RS6040V48G,
        )
        arm_mass_variants.append(
            {
                "axes": [asdict(axis) for axis in variant_drive.axes],
                "case_id": mass_case.case_id,
                "passes": variant_drive.passes,
                "upper_arm_each_kg": upper_arm_mass_kg,
            }
        )
    efficiency_sensitivity = []
    for efficiency in (0.85, 0.90, 0.95):
        assessment = assess_refined_drive(
            trajectory,
            conservative,
            LEADSHINE_ISV2_RS6040V48G,
            efficiency=efficiency,
        )
        efficiency_sensitivity.append(
            {
                "efficiency": efficiency,
                "passes": assessment.passes,
                "worst_peak_torque_nm": max(
                    axis.required_peak_torque_nm for axis in assessment.axes
                ),
                "worst_rms_torque_nm": max(
                    axis.required_rms_torque_nm for axis in assessment.axes
                ),
            }
        )
    maximum_external_joint_inertia = max(
        inertia
        for sample in trajectory.samples
        for inertia in joint_effective_inertias_kg_m2(
            sample.differential, CONSERVATIVE_MASS_CASE
        )
    )
    bench_arm_length_m = 0.280
    bench_arm_mass_kg = 0.250
    bench_arm_inertia = bench_arm_mass_kg * bench_arm_length_m**2 / 3.0
    equivalent_tip_mass = max(
        0.0,
        (maximum_external_joint_inertia - bench_arm_inertia) / bench_arm_length_m**2,
    )
    return {
        "cases": [_case_document(nominal), _case_document(conservative)],
        "candidate_assessment": {
            **_refined_document(candidate_assessment),
            "candidate": asdict(LEADSHINE_ISV2_RS6040V48G),
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
            "shaft, coupling, bushing and belt inertias include geometric estimates",
            "belt tension is a calculated pitch-line difference plus provisional preload",
            "torque-speed and thermal feasibility require manufacturer data and a bench test",
        ],
        "arm_mass_variants": arm_mass_variants,
        "efficiency_sensitivity": efficiency_sensitivity,
        "equivalent_bench_load": {
            "arm_length_m": bench_arm_length_m,
            "arm_mass_kg": bench_arm_mass_kg,
            "arm_uniform_inertia_kg_m2": bench_arm_inertia,
            "maximum_external_joint_inertia_kg_m2": maximum_external_joint_inertia,
            "point_mass_at_arm_tip_kg": equivalent_tip_mass,
            "scope": "inertia_equivalent_only_not_full_delta_load_oracle",
        },
        "legacy_candidate_assessment": {
            "axes": [asdict(axis) for axis in legacy_candidate_assessment.axes],
            "design_factor": legacy_candidate_assessment.design_factor,
            "efficiency": legacy_candidate_assessment.efficiency,
            "maximum_motor_acceleration_rad_s2": (
                legacy_candidate_assessment.maximum_motor_acceleration_rad_s2
            ),
            "maximum_motor_speed_rpm": legacy_candidate_assessment.maximum_motor_speed_rpm,
            "passes": legacy_candidate_assessment.passes,
            "ratio": legacy_candidate_assessment.ratio,
        },
        "model": {
            "design_factor": DESIGN_FACTOR,
            "gravity_m_s2": STANDARD_GRAVITY_M_S2,
            "lower_mass_model": "half_translating_half_equally_knee_lumped",
            "transmission_efficiency": TRANSMISSION_EFFICIENCY,
            "upper_arm_model": "uniform_rigid_link",
        },
        "schema": "delta-robot-p1-dynamic-sizing/v2",
        "source": SELECTED_SOURCE_LABEL,
        "status": "provisional_pass" if convergence < 0.01 else "sampling_not_converged",
        "trajectory": {
            "duration_s": trajectory.duration_s,
            "name": "25-305-25_round_trip_1_hz",
            "sample_count": len(trajectory.samples),
            "sample_period_s": trajectory.sample_period_s,
        },
        "transmissions": [asdict(requirement) for requirement in requirements],
        "transmission_inertia": {
            **asdict(P1_TRANSMISSION_INERTIA),
            "belt_mass_kg": 0.01715,
            "component_assumptions": {
                "bushing": "steel annulus OD 57 mm, ID 20 mm, length 25.4 mm",
                "coupling": "aluminium annulus OD 35 mm, ID 9.525 mm, length 45 mm",
                "input_shaft": "steel solid cylinder D 9.525 mm, length 110 mm",
                "output_shaft": "steel solid cylinder D 20 mm, length 180 mm",
            },
            "density_aluminium_kg_m3": 2700.0,
            "density_steel_kg_m3": 7850.0,
            "measurement_plan": "weigh actual parts and replace geometric estimates",
        },
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
