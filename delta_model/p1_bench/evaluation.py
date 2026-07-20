"""CSV logging and deterministic automatic P1 gate evaluation."""

import csv
import io
import math
from dataclasses import asdict, dataclass
from typing import ClassVar, Literal

from delta_model.p1_bench.drive import TelemetrySample


@dataclass(frozen=True, slots=True)
class P1Thresholds:
    minimum_reversals: int = 1000
    maximum_lost_motion_deg: float = 0.10
    maximum_driver_temperature_c: float = 60.0
    maximum_dc_bus_voltage_v: float = 60.0
    maximum_brake_resistor_load_percent: float = 80.0
    maximum_output_following_error_deg: float = 0.50


@dataclass(frozen=True, slots=True)
class TestRun:
    __test__: ClassVar[bool] = False

    source: Literal["simulation", "hardware"]
    samples: tuple[TelemetrySample, ...]
    reduction_ratio: float
    measured_lost_motion_deg: float
    full_speed_stage_executed: bool


def _validate_run(run: TestRun) -> None:
    if not run.samples:
        raise ValueError("test run must contain telemetry")
    if not math.isfinite(run.reduction_ratio) or run.reduction_ratio <= 0.0:
        raise ValueError("reduction ratio must be finite and positive")
    if not math.isfinite(run.measured_lost_motion_deg) or run.measured_lost_motion_deg < 0.0:
        raise ValueError("lost motion must be finite and non-negative")
    previous = -math.inf
    for sample in run.samples:
        numeric = (
            sample.timestamp_s,
            sample.command_motor_position_rad,
            sample.actual_motor_position_rad,
            sample.actual_motor_velocity_rad_s,
            sample.estimated_motor_torque_nm,
            sample.driver_temperature_c,
            sample.dc_bus_voltage_v,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("telemetry contains a non-finite required value")
        if sample.timestamp_s < previous:
            raise ValueError("telemetry timestamps must be monotonic")
        previous = sample.timestamp_s


def _reversal_count(samples: tuple[TelemetrySample, ...]) -> int:
    last_sign = 0
    reversals = 0
    previous = samples[0].command_motor_position_rad
    for sample in samples[1:]:
        delta = sample.command_motor_position_rad - previous
        sign = 1 if delta > 1e-12 else -1 if delta < -1e-12 else 0
        if sign and last_sign and sign != last_sign:
            reversals += 1
        if sign:
            last_sign = sign
        previous = sample.command_motor_position_rad
    return reversals


def evaluate_p1(
    run: TestRun, thresholds: P1Thresholds | None = None
) -> dict[str, object]:
    """Evaluate one log; simulation can never return a physical pass."""

    _validate_run(run)
    thresholds = thresholds or P1Thresholds()
    reversal_count = _reversal_count(run.samples)
    alarms = sorted({code for sample in run.samples for code in sample.alarm_codes})
    maximum_error_deg = max(
        abs(sample.command_motor_position_rad - sample.actual_motor_position_rad)
        / run.reduction_ratio
        * 180.0
        / math.pi
        for sample in run.samples
    )
    maximum_temperature = max(sample.driver_temperature_c for sample in run.samples)
    maximum_bus_voltage = max(sample.dc_bus_voltage_v for sample in run.samples)
    brake_values = tuple(
        sample.brake_resistor_load_percent
        for sample in run.samples
        if sample.brake_resistor_load_percent is not None
    )
    maximum_brake_load = max(brake_values) if brake_values else None
    checks = {
        "full_speed_stage_executed": run.full_speed_stage_executed,
        "minimum_reversals": reversal_count >= thresholds.minimum_reversals,
        "no_drive_alarms": not alarms,
        "lost_motion_within_limit": (
            run.measured_lost_motion_deg <= thresholds.maximum_lost_motion_deg
        ),
        "following_error_within_limit": (
            maximum_error_deg <= thresholds.maximum_output_following_error_deg
        ),
        "driver_temperature_within_test_limit": (
            maximum_temperature < thresholds.maximum_driver_temperature_c
        ),
        "dc_bus_voltage_within_limit": maximum_bus_voltage <= thresholds.maximum_dc_bus_voltage_v,
        "brake_resistor_load_within_limit": (
            maximum_brake_load is None
            or maximum_brake_load < thresholds.maximum_brake_resistor_load_percent
        ),
    }
    numerical_pass = all(checks.values())
    if numerical_pass and run.source == "hardware":
        disposition = "passed"
    elif numerical_pass:
        disposition = "simulation_only"
    else:
        disposition = "failed"
    return {
        "checks": checks,
        "disposition": disposition,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "metrics": {
            "alarm_codes": alarms,
            "maximum_brake_resistor_load_percent": maximum_brake_load,
            "maximum_dc_bus_voltage_v": maximum_bus_voltage,
            "maximum_driver_temperature_c": maximum_temperature,
            "maximum_output_following_error_deg": maximum_error_deg,
            "measured_lost_motion_deg": run.measured_lost_motion_deg,
            "reversal_count": reversal_count,
            "sample_count": len(run.samples),
        },
        "schema": "delta-robot-p1-bench-report/v1",
        "source": run.source,
        "thresholds": asdict(thresholds),
    }


def telemetry_csv(samples: tuple[TelemetrySample, ...]) -> str:
    """Serialize telemetry with unit-bearing stable column names."""

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        (
            "timestamp_s",
            "stage",
            "command_motor_position_rad",
            "actual_motor_position_rad",
            "actual_motor_velocity_rad_s",
            "estimated_motor_torque_nm",
            "driver_temperature_c",
            "dc_bus_voltage_v",
            "brake_resistor_load_percent",
            "alarm_codes_hex",
        )
    )
    for sample in samples:
        writer.writerow(
            (
                sample.timestamp_s,
                sample.stage,
                sample.command_motor_position_rad,
                sample.actual_motor_position_rad,
                sample.actual_motor_velocity_rad_s,
                sample.estimated_motor_torque_nm,
                sample.driver_temperature_c,
                sample.dc_bus_voltage_v,
                (
                    ""
                    if sample.brake_resistor_load_percent is None
                    else sample.brake_resistor_load_percent
                ),
                "|".join(f"0x{code:04X}" for code in sample.alarm_codes),
            )
        )
    return output.getvalue()
