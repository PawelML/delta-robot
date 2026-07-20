"""Provisional DIY geometry candidates and the P0-selected configuration."""

import math
from dataclasses import dataclass

from delta_model.geometry import DeltaGeometry


@dataclass(frozen=True, slots=True)
class GeometryCandidate:
    """Named geometry considered by the P0 deterministic screening."""

    candidate_id: str
    geometry: DeltaGeometry
    rationale: str


@dataclass(frozen=True, slots=True)
class UsefulCylinder:
    """Cylindrical Cartesian region selected for trajectory work."""

    radius_m: float
    height_m: float
    center_z_m: float


def _geometry(
    base_radius_m: float,
    platform_radius_m: float,
    upper_length_m: float,
    lower_length_m: float,
) -> DeltaGeometry:
    return DeltaGeometry(
        base_joint_radius_m=base_radius_m,
        platform_joint_radius_m=platform_radius_m,
        upper_arm_length_m=upper_length_m,
        lower_arm_length_m=lower_length_m,
        min_joint_angle_rad=math.radians(-45.0),
        max_joint_angle_rad=math.radians(80.0),
    )


GEOMETRY_CANDIDATES = (
    GeometryCandidate(
        candidate_id="compact_400",
        geometry=_geometry(0.180, 0.055, 0.200, 0.400),
        rationale="smallest envelope and shortest moving upper arm",
    ),
    GeometryCandidate(
        candidate_id="balanced_430",
        geometry=_geometry(0.210, 0.060, 0.240, 0.430),
        rationale="moderate proportional dimensions within the provisional rod range",
    ),
    GeometryCandidate(
        candidate_id="reach_optimized_450",
        geometry=_geometry(0.180, 0.065, 0.280, 0.450),
        rationale="parameter-search candidate for a full 400 mm useful diameter",
    ),
)

SELECTED_CANDIDATE_ID = "reach_optimized_450"
SELECTED_GEOMETRY = next(
    candidate.geometry
    for candidate in GEOMETRY_CANDIDATES
    if candidate.candidate_id == SELECTED_CANDIDATE_ID
)
# Set from the reproducible geometry-comparison report. The screening script
# verifies this value still matches its best refined placement.
SELECTED_USEFUL_CYLINDER = UsefulCylinder(radius_m=0.200, height_m=0.150, center_z_m=-0.347)
SELECTED_SOURCE_LABEL = "p0_selected_diy_reach_optimized_450"
