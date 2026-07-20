import json
import math
from collections.abc import Sequence
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from typing import cast

import pytest

from delta_model.p1_bench.artifacts import simulation_artifacts
from delta_model.p1_bench.commands import (
    DriveCommand,
    generate_axis_commands,
    generate_reversal_commands,
)
from delta_model.p1_bench.drive import SimulatedDrive, TelemetrySample
from delta_model.p1_bench.evaluation import TestRun, evaluate_p1, telemetry_csv
from delta_model.p1_bench.modbus import (
    LeadshineDiagnostics,
    LeadshineScaling,
    signed_16,
    signed_32_high_low,
)
from delta_model.trajectory import generate_trajectory


def test_axis_commands_retain_samples_and_scale_time_derivatives() -> None:
    trajectory = generate_trajectory()
    full = generate_axis_commands(trajectory, axis=2)
    quarter = generate_axis_commands(trajectory, axis=2, speed_fraction=0.25)

    assert len(full) == len(quarter) == 1001
    assert full[-1].timestamp_s == pytest.approx(1.0)
    assert quarter[-1].timestamp_s == pytest.approx(4.0)
    assert quarter[250].motor_position_rad == pytest.approx(full[250].motor_position_rad)
    assert quarter[250].motor_velocity_rad_s == pytest.approx(
        0.25 * full[250].motor_velocity_rad_s
    )
    assert quarter[250].motor_acceleration_rad_s2 == pytest.approx(
        0.25**2 * full[250].motor_acceleration_rad_s2
    )


def test_reversal_generator_produces_requested_direction_changes() -> None:
    commands = generate_reversal_commands(
        start_time_s=0.0,
        start_motor_position_rad=0.0,
        low_motor_position_rad=-1.0,
        high_motor_position_rad=1.0,
        reversals=1000,
        half_period_s=0.5,
    )

    assert len(commands) == 1002
    signs = [
        math.copysign(1.0, second.motor_position_rad - first.motor_position_rad)
        for first, second in pairwise(commands)
    ]
    assert sum(left != right for left, right in pairwise(signs)) == 1000


def test_simulator_requires_enable_and_rejects_time_reversal() -> None:
    drive = SimulatedDrive()
    command = DriveCommand(1.0, 1.0, 0.0, 0.0, "test")
    with pytest.raises(RuntimeError, match="enabled"):
        drive.apply(command)
    drive.enable()
    first = drive.apply(command)
    with pytest.raises(ValueError, match="monotonic"):
        drive.apply(DriveCommand(0.0, 0.0, 0.0, 0.0, "test"))
    assert first.actual_motor_position_rad > 0.99


def test_simulator_exposes_injected_alarm_temperature_and_bus_voltage() -> None:
    drive = SimulatedDrive(injected_alarms={1: (0x120,)})
    drive.enable()
    drive.apply(DriveCommand(0.0, 0.0, 0.0, 0.0, "test"))
    sample = drive.apply(DriveCommand(0.1, 0.1, 1.0, 10.0, "test"))

    assert sample.alarm_codes == (0x120,)
    assert sample.driver_temperature_c >= 22.0
    assert sample.dc_bus_voltage_v >= 48.0


class FakeModbusClient:
    def __init__(self, values: dict[int, tuple[int, ...]]) -> None:
        self.values = values

    def read_holding_registers(self, address: int, count: int) -> Sequence[int]:
        return self.values[address][:count]


def test_leadshine_decoder_uses_high_word_first_and_signed_values() -> None:
    assert signed_16(0xFFFE) == -2
    assert signed_32_high_low(0xFFFF, 0xFF9C) == -100
    client = FakeModbusClient(
        {
            0x0B03: (0,),
            0x0B07: (100,),
            0x0B08: (50,),
            0x0B09: (0xFFFE,),
            0x0B0A: (48,),
            0x0B0B: (35,),
            0x0B0F: (20,),
            0x0B14: (0x0000, 0x1388),
            0x0B16: (0x0000, 0x09C4),
            0x0B18: (0xFFFF, 0xFF9C),
        }
    )
    diagnostics = LeadshineDiagnostics(
        client,
        LeadshineScaling(10000.0, 1.0, 0.001, 0.01, 1.0),
    ).read()

    assert diagnostics.speed_rad_s == pytest.approx(-2.0 * 2.0 * math.pi / 60.0)
    assert diagnostics.command_position_rad == pytest.approx(math.pi)
    assert diagnostics.actual_position_rad == pytest.approx(math.pi / 2.0)
    assert diagnostics.position_deviation_rad == pytest.approx(-0.02 * math.pi)


def _passing_samples() -> tuple[TelemetrySample, ...]:
    positions = [0.0]
    positions.extend(1.0 if index % 2 == 0 else -1.0 for index in range(1002))
    return tuple(
        TelemetrySample(
            timestamp_s=float(index),
            stage="hardware_test",
            command_motor_position_rad=position,
            actual_motor_position_rad=position,
            actual_motor_velocity_rad_s=0.0,
            estimated_motor_torque_nm=0.0,
            driver_temperature_c=40.0,
            dc_bus_voltage_v=48.0,
            brake_resistor_load_percent=20.0,
            alarm_codes=(),
        )
        for index, position in enumerate(positions)
    )


def test_same_good_metrics_pass_hardware_but_not_simulation() -> None:
    hardware = TestRun("hardware", _passing_samples(), 5.0, 0.05, True)
    simulation = replace(hardware, source="simulation")

    assert evaluate_p1(hardware)["disposition"] == "passed"
    assert evaluate_p1(simulation)["disposition"] == "simulation_only"


def test_alarm_names_failed_check_and_csv_keeps_alarm_code() -> None:
    samples = list(_passing_samples())
    samples[10] = replace(samples[10], alarm_codes=(0x120,))
    report = evaluate_p1(TestRun("hardware", tuple(samples), 5.0, 0.05, True))

    assert report["disposition"] == "failed"
    assert "no_drive_alarms" in cast(list[str], report["failed_checks"])
    assert "0x0120" in telemetry_csv(tuple(samples))


def test_simulation_artifacts_match_committed_files() -> None:
    csv_content, report = simulation_artifacts()
    root = Path(__file__).resolve().parents[1]

    assert csv_content == (root / "artifacts/p1_bench_simulation.csv").read_text(
        encoding="utf-8"
    )
    committed = json.loads(
        (root / "artifacts/p1_bench_simulation.json").read_text(encoding="utf-8")
    )
    assert json.loads(json.dumps(report)) == committed
    assert report["disposition"] == "simulation_only"
