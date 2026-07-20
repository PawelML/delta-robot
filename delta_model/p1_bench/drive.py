"""Drive protocol and deterministic no-hardware P1 simulator."""

import math
from dataclasses import dataclass
from typing import Protocol

from delta_model.p1_bench.commands import DriveCommand


@dataclass(frozen=True, slots=True)
class TelemetrySample:
    """One command/feedback sample with explicit engineering units."""

    timestamp_s: float
    stage: str
    command_motor_position_rad: float
    actual_motor_position_rad: float
    actual_motor_velocity_rad_s: float
    estimated_motor_torque_nm: float
    driver_temperature_c: float
    dc_bus_voltage_v: float
    brake_resistor_load_percent: float | None
    alarm_codes: tuple[int, ...]


class Drive(Protocol):
    """Minimum interface shared by simulator and future hardware transport."""

    def enable(self) -> None: ...

    def disable(self) -> None: ...

    def apply(self, command: DriveCommand) -> TelemetrySample: ...


class SimulatedDrive:
    """Deterministic second-order test double; not a motor-physics oracle."""

    def __init__(
        self,
        *,
        natural_frequency_rad_s: float = 1500.0,
        damping_ratio: float = 1.0,
        equivalent_motor_inertia_kg_m2: float = 0.00045,
        bus_voltage_v: float = 48.0,
        ambient_temperature_c: float = 22.0,
        injected_alarms: dict[int, tuple[int, ...]] | None = None,
    ) -> None:
        values = (
            natural_frequency_rad_s,
            damping_ratio,
            equivalent_motor_inertia_kg_m2,
            bus_voltage_v,
            ambient_temperature_c,
        )
        if not all(math.isfinite(value) and value > 0.0 for value in values):
            raise ValueError("simulator parameters must be finite and positive")
        self._natural_frequency = natural_frequency_rad_s
        self._damping_ratio = damping_ratio
        self._inertia = equivalent_motor_inertia_kg_m2
        self._nominal_bus_voltage = bus_voltage_v
        self._ambient_temperature = ambient_temperature_c
        self._alarms = injected_alarms or {}
        self._enabled = False
        self._timestamp_s = 0.0
        self._position_rad = 0.0
        self._velocity_rad_s = 0.0
        self._temperature_c = ambient_temperature_c
        self._sample_index = 0

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def apply(self, command: DriveCommand) -> TelemetrySample:
        if not self._enabled:
            raise RuntimeError("drive must be enabled before applying commands")
        if command.timestamp_s < self._timestamp_s:
            raise ValueError("command timestamps must be monotonic")
        if self._sample_index == 0 and command.timestamp_s == 0.0:
            self._position_rad = command.motor_position_rad
        elapsed = command.timestamp_s - self._timestamp_s
        error = self._position_rad - command.motor_position_rad
        if self._damping_ratio == 1.0:
            coefficient = self._velocity_rad_s + self._natural_frequency * error
            decay = math.exp(-self._natural_frequency * elapsed)
            error = (error + coefficient * elapsed) * decay
            self._velocity_rad_s = (
                self._velocity_rad_s
                - self._natural_frequency * coefficient * elapsed
            ) * decay
            self._position_rad = command.motor_position_rad + error
        else:
            substeps = max(1, math.ceil(elapsed * self._natural_frequency / 0.05))
            step = elapsed / substeps
            for _ in range(substeps):
                acceleration = (
                    -self._natural_frequency**2
                    * (self._position_rad - command.motor_position_rad)
                    - 2.0
                    * self._damping_ratio
                    * self._natural_frequency
                    * self._velocity_rad_s
                )
                self._velocity_rad_s += acceleration * step
                self._position_rad += self._velocity_rad_s * step
        torque = self._inertia * command.motor_acceleration_rad_s2
        mechanical_power = torque * self._velocity_rad_s
        peak_regenerated_power = max(0.0, -mechanical_power)
        heating = 0.018 * torque**2
        cooling = 0.025 * (self._temperature_c - self._ambient_temperature)
        self._temperature_c += (heating - cooling) * elapsed
        self._timestamp_s = command.timestamp_s
        bus_rise = min(8.0, 0.025 * peak_regenerated_power)
        brake_load = min(100.0, peak_regenerated_power / 100.0 * 100.0)
        alarms = self._alarms.get(self._sample_index, ())
        self._sample_index += 1
        return TelemetrySample(
            timestamp_s=command.timestamp_s,
            stage=command.stage,
            command_motor_position_rad=command.motor_position_rad,
            actual_motor_position_rad=self._position_rad,
            actual_motor_velocity_rad_s=self._velocity_rad_s,
            estimated_motor_torque_nm=torque,
            driver_temperature_c=self._temperature_c,
            dc_bus_voltage_v=self._nominal_bus_voltage + bus_rise,
            brake_resistor_load_percent=brake_load,
            alarm_codes=alarms,
        )
