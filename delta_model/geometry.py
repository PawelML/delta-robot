"""Validated geometry contract for the symmetric rotary delta robot."""

import math
from dataclasses import dataclass


class GeometryValidationError(ValueError):
    """Raised when dimensions cannot describe a valid P0 geometry contract."""


@dataclass(frozen=True, slots=True)
class DeltaGeometry:
    """Radius-based delta geometry in SI units."""

    base_joint_radius_m: float
    platform_joint_radius_m: float
    upper_arm_length_m: float
    lower_arm_length_m: float
    min_joint_angle_rad: float
    max_joint_angle_rad: float

    def __post_init__(self) -> None:
        lengths = {
            "base_joint_radius_m": self.base_joint_radius_m,
            "platform_joint_radius_m": self.platform_joint_radius_m,
            "upper_arm_length_m": self.upper_arm_length_m,
            "lower_arm_length_m": self.lower_arm_length_m,
        }
        for name, value in lengths.items():
            if not math.isfinite(value) or value <= 0.0:
                raise GeometryValidationError(f"{name} must be finite and greater than zero")

        limits = (self.min_joint_angle_rad, self.max_joint_angle_rad)
        if not all(math.isfinite(limit) for limit in limits):
            raise GeometryValidationError("joint-angle limits must be finite")
        if self.min_joint_angle_rad >= self.max_joint_angle_rad:
            raise GeometryValidationError(
                "min_joint_angle_rad must be less than max_joint_angle_rad"
            )
