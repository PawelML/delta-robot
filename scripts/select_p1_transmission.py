"""Generate the deterministic P1 transmission selection artifact."""

import json
from pathlib import Path

from delta_model.drive_sizing import LEADSHINE_ISV2_RS6040V48G, assess_refined_drive
from delta_model.dynamics import CONSERVATIVE_MASS_CASE, evaluate_dynamic_case
from delta_model.trajectory import generate_trajectory
from delta_model.transmission import transmission_document


def main() -> None:
    """Evaluate the selected trajectory and write the transmission report."""

    trajectory = generate_trajectory()
    dynamic = evaluate_dynamic_case(trajectory, CONSERVATIVE_MASS_CASE)
    candidate = assess_refined_drive(trajectory, dynamic, LEADSHINE_ISV2_RS6040V48G)
    peak_design_belt_torque = (
        max(axis.peak_belt_tension_difference_n for axis in candidate.axes)
        * (18 * 0.005 / (2.0 * 3.141592653589793))
        * candidate.design_factor
    )
    document = transmission_document(
        maximum_motor_speed_rpm=candidate.maximum_motor_speed_rpm,
        peak_design_transmitted_torque_nm=peak_design_belt_torque,
        maximum_trajectory_belt_power_w=candidate.maximum_belt_power_w,
    )
    output = Path(__file__).resolve().parents[1] / "artifacts/p1_transmission_selection.json"
    output.write_text(
        json.dumps(document, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
