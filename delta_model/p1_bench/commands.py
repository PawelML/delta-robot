"""Transport-neutral P1 motor-position command generators."""

import math
from dataclasses import dataclass

from delta_model.trajectory import Trajectory, TrajectorySample


@dataclass(frozen=True, slots=True)
class DriveCommand:
    """One absolute motor command in SI units."""

    timestamp_s: float
    motor_position_rad: float
    motor_velocity_rad_s: float
    motor_acceleration_rad_s2: float
    stage: str

    def __post_init__(self) -> None:
        values = (
            self.timestamp_s,
            self.motor_position_rad,
            self.motor_velocity_rad_s,
            self.motor_acceleration_rad_s2,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("drive command values must be finite")
        if self.timestamp_s < 0.0 or not self.stage.strip():
            raise ValueError("command timestamp and stage are invalid")


def _axis_state(sample: TrajectorySample, axis_index: int) -> tuple[float, float, float]:
    angles = sample.differential.inverse_result.angles
    rates = sample.joint_rates
    accelerations = sample.joint_accelerations
    angle_values = (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad)
    rate_values = (rates.theta_1_rad_s, rates.theta_2_rad_s, rates.theta_3_rad_s)
    acceleration_values = (
        accelerations.theta_1_rad_s2,
        accelerations.theta_2_rad_s2,
        accelerations.theta_3_rad_s2,
    )
    return (
        angle_values[axis_index],
        rate_values[axis_index],
        acceleration_values[axis_index],
    )


def generate_axis_commands(
    trajectory: Trajectory,
    *,
    axis: int,
    ratio: float = 5.0,
    speed_fraction: float = 1.0,
    start_time_s: float = 0.0,
) -> tuple[DriveCommand, ...]:
    """Map an authoritative delta trajectory axis to absolute motor commands."""

    if axis not in (1, 2, 3):
        raise ValueError("axis must be 1, 2 or 3")
    if not math.isfinite(ratio) or ratio <= 0.0:
        raise ValueError("ratio must be finite and positive")
    if not math.isfinite(speed_fraction) or not 0.0 < speed_fraction <= 1.0:
        raise ValueError("speed_fraction must lie in (0, 1]")
    if not math.isfinite(start_time_s) or start_time_s < 0.0:
        raise ValueError("start_time_s must be finite and non-negative")
    commands = []
    for sample in trajectory.samples:
        position, velocity, acceleration = _axis_state(sample, axis - 1)
        commands.append(
            DriveCommand(
                timestamp_s=start_time_s + sample.time_s / speed_fraction,
                motor_position_rad=ratio * position,
                motor_velocity_rad_s=ratio * velocity * speed_fraction,
                motor_acceleration_rad_s2=ratio * acceleration * speed_fraction**2,
                stage=f"trajectory_{speed_fraction:.2f}x",
            )
        )
    return tuple(commands)


def generate_reversal_commands(
    *,
    start_time_s: float,
    start_motor_position_rad: float,
    low_motor_position_rad: float,
    high_motor_position_rad: float,
    reversals: int,
    half_period_s: float,
) -> tuple[DriveCommand, ...]:
    """Generate endpoint commands for a repeatable reversal endurance segment."""

    values = (
        start_time_s,
        start_motor_position_rad,
        low_motor_position_rad,
        high_motor_position_rad,
        half_period_s,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("reversal inputs must be finite")
    if start_time_s < 0.0 or reversals < 1 or half_period_s <= 0.0:
        raise ValueError("reversal count, time and period are invalid")
    if not low_motor_position_rad < high_motor_position_rad:
        raise ValueError("low reversal position must be below high position")
    commands = [
        DriveCommand(
            timestamp_s=start_time_s,
            motor_position_rad=start_motor_position_rad,
            motor_velocity_rad_s=0.0,
            motor_acceleration_rad_s2=0.0,
            stage="endurance_reversals",
        )
    ]
    target_high = start_motor_position_rad <= (low_motor_position_rad + high_motor_position_rad) / 2
    previous = start_motor_position_rad
    for index in range(reversals + 1):
        target = high_motor_position_rad if target_high else low_motor_position_rad
        velocity = (target - previous) / half_period_s
        commands.append(
            DriveCommand(
                timestamp_s=start_time_s + (index + 1) * half_period_s,
                motor_position_rad=target,
                motor_velocity_rad_s=velocity,
                motor_acceleration_rad_s2=0.0,
                stage="endurance_reversals",
            )
        )
        target_high = not target_high
        previous = target
    return tuple(commands)
