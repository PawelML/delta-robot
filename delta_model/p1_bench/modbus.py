"""Injected-client decoder for current Leadshine iSV2-RS status registers."""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class ModbusRegisterClient(Protocol):
    def read_holding_registers(self, address: int, count: int) -> Sequence[int]: ...


@dataclass(frozen=True, slots=True)
class LeadshineScaling:
    """Revision-specific scaling that hardware integration must confirm."""

    command_units_per_revolution: float
    speed_rpm_per_count: float
    torque_nm_per_count: float
    current_a_per_count: float
    overload_percent_per_count: float

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value) and value > 0.0
            for value in (
                self.command_units_per_revolution,
                self.speed_rpm_per_count,
                self.torque_nm_per_count,
                self.current_a_per_count,
                self.overload_percent_per_count,
            )
        ):
            raise ValueError("Leadshine scaling values must be finite and positive")


@dataclass(frozen=True, slots=True)
class LeadshineDiagnosticSnapshot:
    alarm_code: int
    speed_rad_s: float
    torque_nm: float
    current_a: float
    dc_bus_voltage_v: float
    driver_temperature_c: float
    overload_percent: float
    command_position_rad: float
    actual_position_rad: float
    position_deviation_rad: float


def signed_16(value: int) -> int:
    if not 0 <= value <= 0xFFFF:
        raise ValueError("Modbus word must lie in 0..65535")
    return value - 0x10000 if value & 0x8000 else value


def signed_32_high_low(high_word: int, low_word: int) -> int:
    if not 0 <= high_word <= 0xFFFF or not 0 <= low_word <= 0xFFFF:
        raise ValueError("Modbus words must lie in 0..65535")
    value = (high_word << 16) | low_word
    return value - 0x100000000 if value & 0x80000000 else value


class LeadshineDiagnostics:
    """Read one coherent-enough diagnostic snapshot through an injected client."""

    def __init__(self, client: ModbusRegisterClient, scaling: LeadshineScaling) -> None:
        self._client = client
        self._scaling = scaling

    def _words(self, address: int, count: int) -> tuple[int, ...]:
        values = tuple(self._client.read_holding_registers(address, count))
        if len(values) != count or not all(0 <= value <= 0xFFFF for value in values):
            raise ValueError(f"invalid Modbus response at 0x{address:04X}")
        return values

    def _signed_word(self, address: int) -> int:
        return signed_16(self._words(address, 1)[0])

    def _signed_dword(self, address: int) -> int:
        high, low = self._words(address, 2)
        return signed_32_high_low(high, low)

    def read(self) -> LeadshineDiagnosticSnapshot:
        units_to_rad = 2.0 * math.pi / self._scaling.command_units_per_revolution
        return LeadshineDiagnosticSnapshot(
            alarm_code=self._words(0x0B03, 1)[0],
            speed_rad_s=(
                self._signed_word(0x0B09)
                * self._scaling.speed_rpm_per_count
                * 2.0
                * math.pi
                / 60.0
            ),
            torque_nm=self._signed_word(0x0B07) * self._scaling.torque_nm_per_count,
            current_a=self._signed_word(0x0B08) * self._scaling.current_a_per_count,
            dc_bus_voltage_v=float(self._words(0x0B0A, 1)[0]),
            driver_temperature_c=float(self._words(0x0B0B, 1)[0]),
            overload_percent=(
                self._words(0x0B0F, 1)[0] * self._scaling.overload_percent_per_count
            ),
            command_position_rad=self._signed_dword(0x0B14) * units_to_rad,
            actual_position_rad=self._signed_dword(0x0B16) * units_to_rad,
            position_deviation_rad=self._signed_dword(0x0B18) * units_to_rad,
        )
