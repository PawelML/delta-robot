"""Write signed budget robot shoulder loads for comparison with bench telemetry."""

import argparse
import csv
import sys
from dataclasses import astuple

from delta_model.budget_sizing import budget_output_load
from delta_model.dynamics import joint_effective_inertias_kg_m2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload-kg", required=True, type=float)
    parser.add_argument("--cycle-s", required=True, type=float)
    args = parser.parse_args()

    trajectory, dynamic = budget_output_load(
        payload_kg=args.payload_kg, cycle_duration_s=args.cycle_s
    )
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(
        (
            "time_s",
            "axis",
            "angle_rad",
            "speed_rad_s",
            "acceleration_rad_s2",
            "external_torque_nm",
            "external_inertia_kg_m2",
        )
    )
    for sample, torque in zip(trajectory.samples, dynamic.torques_nm, strict=True):
        inertia = joint_effective_inertias_kg_m2(sample.differential, dynamic.mass_case)
        states = zip(
            astuple(sample.angles),
            astuple(sample.joint_rates),
            astuple(sample.joint_accelerations),
            torque,
            inertia,
            strict=True,
        )
        for axis, state in enumerate(states, start=1):
            writer.writerow((sample.time_s, axis, *state))


if __name__ == "__main__":
    main()
