"""Deterministic no-hardware P1 simulation artifact generation."""

import math

from delta_model.p1_bench.commands import (
    generate_axis_commands,
    generate_reversal_commands,
)
from delta_model.p1_bench.drive import SimulatedDrive
from delta_model.p1_bench.evaluation import TestRun, evaluate_p1, telemetry_csv
from delta_model.trajectory import generate_trajectory


def simulation_artifacts() -> tuple[str, dict[str, object]]:
    """Return reproducible CSV and JSON report content."""

    trajectory = generate_trajectory()
    full_speed = generate_axis_commands(trajectory, axis=2)
    positions = tuple(command.motor_position_rad for command in full_speed)
    endurance = generate_reversal_commands(
        start_time_s=full_speed[-1].timestamp_s,
        start_motor_position_rad=full_speed[-1].motor_position_rad,
        low_motor_position_rad=min(positions),
        high_motor_position_rad=max(positions),
        reversals=1000,
        half_period_s=0.5,
    )
    commands = (*full_speed, *endurance[1:])
    drive = SimulatedDrive()
    drive.enable()
    samples = tuple(drive.apply(command) for command in commands)
    drive.disable()
    run = TestRun(
        source="simulation",
        samples=samples,
        reduction_ratio=5.0,
        measured_lost_motion_deg=0.04,
        full_speed_stage_executed=True,
    )
    report = evaluate_p1(run)
    report["command_plan"] = {
        "axis": 2,
        "endurance_half_period_s": 0.5,
        "requested_endurance_reversals": 1000,
        "trajectory": "25-305-25_round_trip_1_hz",
    }
    report["limitations"] = [
        "simulation proves software plumbing only and cannot pass physical P1",
        "thermal, bus and tracking responses are deterministic test-double behaviour",
        "hardware command transport and Modbus polling remain unimplemented",
    ]
    if any(
        not math.isfinite(value)
        for sample in samples
        for value in (
            sample.actual_motor_position_rad,
            sample.driver_temperature_c,
            sample.dc_bus_voltage_v,
        )
    ):
        raise RuntimeError("simulator emitted non-finite telemetry")
    return telemetry_csv(samples), report
