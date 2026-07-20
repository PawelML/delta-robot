"""Generate the deterministic P1 transmission selection artifact."""

import json
from pathlib import Path

from delta_model.drive_sizing import LEADSHINE_ISV2_RS6040V48G, assess_motor_candidate
from delta_model.dynamics import CONSERVATIVE_MASS_CASE, evaluate_dynamic_case
from delta_model.trajectory import generate_trajectory
from delta_model.transmission import transmission_document


def main() -> None:
    """Evaluate the selected trajectory and write the transmission report."""

    trajectory = generate_trajectory()
    dynamic = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    candidate = assess_motor_candidate(trajectory, dynamic, LEADSHINE_ISV2_RS6040V48G)
    maximum_belt_power = max(
        abs(torque * rate) / candidate.efficiency
        for sample, torque_row in zip(trajectory.samples, dynamic.torques_nm, strict=True)
        for torque, rate in zip(
            torque_row,
            (
                sample.joint_rates.theta_1_rad_s,
                sample.joint_rates.theta_2_rad_s,
                sample.joint_rates.theta_3_rad_s,
            ),
            strict=True,
        )
    )
    document = transmission_document(
        maximum_motor_speed_rpm=candidate.maximum_motor_speed_rpm,
        peak_design_motor_torque_nm=max(
            axis.required_peak_torque_nm for axis in candidate.axes
        ),
        maximum_trajectory_belt_power_w=maximum_belt_power,
    )
    output = Path(__file__).resolve().parents[1] / "artifacts/p1_transmission_selection.json"
    output.write_text(
        json.dumps(document, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
