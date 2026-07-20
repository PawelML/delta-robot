"""Typed values that encode the coordinate and angle conventions from the P0 spec."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class CartesianPosition:
    """Platform-center position in the base frame, expressed in metres."""

    x_m: float
    y_m: float
    z_m: float


@dataclass(frozen=True, slots=True)
class JointAngles:
    """Actuated shoulder angles for arms 1, 2 and 3, expressed in radians."""

    theta_1_rad: float
    theta_2_rad: float
    theta_3_rad: float


class AssemblyMode(StrEnum):
    """Explicit physical branch for the symmetric rotary delta assembly."""

    KNEE_OUT_PLATFORM_BELOW = "knee_out_platform_below"
