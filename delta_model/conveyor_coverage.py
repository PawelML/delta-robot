"""Application-shaped P0 coverage evidence for the existing conveyor."""

import math
from collections.abc import Callable
from dataclasses import dataclass

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.design_geometry import ConveyorFootprint, UsefulCylinder
from delta_model.geometry import DeltaGeometry
from delta_model.geometry_selection import DESIGN_SINGULARITY_MARGIN, JOINT_LIMIT_RESERVE_RAD
from delta_model.workspace import (
    WorkspaceClassification,
    WorkspaceGrid,
    WorkspacePoint,
    sample_workspace,
)


@dataclass(frozen=True, slots=True)
class ConveyorSampling:
    """Inclusive rectangular-prism sampling counts."""

    x_count: int
    y_count: int
    z_count: int

    @property
    def point_count(self) -> int:
        return self.x_count * self.y_count * self.z_count


@dataclass(frozen=True, slots=True)
class ConveyorCoverage:
    """Containment, classifications and worst sampled design margins."""

    corner_radius_m: float
    radial_reserve_m: float
    contained_in_useful_cylinder: bool
    sampling: ConveyorSampling
    reachable_count: int
    joint_limited_count: int
    unreachable_count: int
    practically_usable_count: int
    minimum_singularity_margin: float | None
    minimum_joint_limit_margin_rad: float | None
    weakest_singularity_position: CartesianPosition | None
    weakest_joint_position: CartesianPosition | None
    passes: bool


DEFAULT_CONVEYOR_SAMPLING = ConveyorSampling(x_count=31, y_count=21, z_count=16)


def _validate_footprint(footprint: ConveyorFootprint) -> None:
    values = (
        footprint.length_m,
        footprint.width_m,
        footprint.center_x_m,
        footprint.center_y_m,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("conveyor footprint values must be finite")
    if footprint.length_m <= 0.0 or footprint.width_m <= 0.0:
        raise ValueError("conveyor footprint dimensions must be positive")


def footprint_corner_radius(footprint: ConveyorFootprint) -> float:
    """Return the farthest XY corner radius from the robot centre."""

    _validate_footprint(footprint)
    x_extent = abs(footprint.center_x_m) + footprint.length_m / 2.0
    y_extent = abs(footprint.center_y_m) + footprint.width_m / 2.0
    return math.hypot(x_extent, y_extent)


def _minimum_point(
    points: tuple[WorkspacePoint, ...],
    value: Callable[[WorkspacePoint], float | None],
) -> tuple[float | None, CartesianPosition | None]:
    candidates: list[tuple[float, CartesianPosition]] = []
    for point in points:
        scalar = value(point)
        if scalar is not None:
            candidates.append((scalar, point.position))
    if not candidates:
        return None, None
    return min(candidates, key=lambda candidate: candidate[0])


def evaluate_conveyor_coverage(
    geometry: DeltaGeometry,
    footprint: ConveyorFootprint,
    cylinder: UsefulCylinder,
    sampling: ConveyorSampling = DEFAULT_CONVEYOR_SAMPLING,
) -> ConveyorCoverage:
    """Evaluate the complete rectangular prism against accepted P0 reserves."""

    _validate_footprint(footprint)
    if not all(
        math.isfinite(value)
        for value in (cylinder.radius_m, cylinder.height_m, cylinder.center_z_m)
    ):
        raise ValueError("useful cylinder values must be finite")
    if cylinder.radius_m <= 0.0 or cylinder.height_m <= 0.0:
        raise ValueError("useful cylinder dimensions must be positive")

    grid = WorkspaceGrid(
        x_min_m=footprint.center_x_m - footprint.length_m / 2.0,
        x_max_m=footprint.center_x_m + footprint.length_m / 2.0,
        x_count=sampling.x_count,
        y_min_m=footprint.center_y_m - footprint.width_m / 2.0,
        y_max_m=footprint.center_y_m + footprint.width_m / 2.0,
        y_count=sampling.y_count,
        z_min_m=cylinder.center_z_m - cylinder.height_m / 2.0,
        z_max_m=cylinder.center_z_m + cylinder.height_m / 2.0,
        z_count=sampling.z_count,
    )
    sample = sample_workspace(geometry, grid, AssemblyMode.KNEE_OUT_PLATFORM_BELOW)
    corner_radius_m = footprint_corner_radius(footprint)
    radial_reserve_m = cylinder.radius_m - corner_radius_m

    def singularity(point: WorkspacePoint) -> float | None:
        return (
            point.singularity_metrics.singularity_margin
            if point.singularity_metrics is not None
            else None
        )

    def joint_margin(point: WorkspacePoint) -> float | None:
        if point.angles is None:
            return None
        return min(
            min(
                angle - geometry.min_joint_angle_rad,
                geometry.max_joint_angle_rad - angle,
            )
            for angle in (
                point.angles.theta_1_rad,
                point.angles.theta_2_rad,
                point.angles.theta_3_rad,
            )
        )

    minimum_singularity, weakest_singularity = _minimum_point(sample.points, singularity)
    minimum_joint, weakest_joint = _minimum_point(sample.points, joint_margin)
    all_reachable = sample.summary.reachable_count == sample.summary.total_count
    all_practically_usable = (
        sample.summary.practically_usable_count == sample.summary.total_count
    )
    margins_pass = (
        minimum_singularity is not None
        and minimum_singularity >= DESIGN_SINGULARITY_MARGIN
        and minimum_joint is not None
        and minimum_joint >= JOINT_LIMIT_RESERVE_RAD
    )
    return ConveyorCoverage(
        corner_radius_m=corner_radius_m,
        radial_reserve_m=radial_reserve_m,
        contained_in_useful_cylinder=radial_reserve_m >= 0.0,
        sampling=sampling,
        reachable_count=sum(
            point.classification is WorkspaceClassification.REACHABLE
            for point in sample.points
        ),
        joint_limited_count=sample.summary.joint_limited_count,
        unreachable_count=sample.summary.unreachable_count,
        practically_usable_count=sample.summary.practically_usable_count,
        minimum_singularity_margin=minimum_singularity,
        minimum_joint_limit_margin_rad=minimum_joint,
        weakest_singularity_position=weakest_singularity,
        weakest_joint_position=weakest_joint,
        passes=(
            radial_reserve_m >= 0.0
            and all_reachable
            and all_practically_usable
            and margins_pass
        ),
    )
