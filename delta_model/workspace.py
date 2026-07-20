"""Deterministic Cartesian workspace sampling using the authoritative IK solver."""

import math
from dataclasses import dataclass, replace
from enum import StrEnum

from delta_model.conventions import AssemblyMode, CartesianPosition, JointAngles
from delta_model.differential_kinematics import (
    PRACTICALLY_USABLE_MARGIN,
    SingularityMetrics,
    differential_kinematics,
)
from delta_model.errors import AssemblyConstraintError, JointLimitError
from delta_model.geometry import DeltaGeometry
from delta_model.inverse_kinematics import (
    AmbiguousAssemblyError,
    DegeneratePositionError,
    UnreachablePositionError,
    inverse_kinematics,
)


class GridValidationError(ValueError):
    """Raised when workspace bounds or sample counts do not define a finite grid."""


class WorkspaceClassification(StrEnum):
    """Three visualizer-facing workspace classes."""

    REACHABLE = "reachable"
    JOINT_LIMITED = "joint_limited"
    UNREACHABLE = "unreachable"


class WorkspaceReason(StrEnum):
    """Diagnostic reason behind a visualizer-facing classification."""

    REACHABLE = "reachable"
    JOINT_LIMIT = "joint_limit"
    GEOMETRIC_UNREACHABLE = "geometric_unreachable"
    DEGENERATE_BOUNDARY = "degenerate_boundary"
    ASSEMBLY_CONSTRAINT = "assembly_constraint"
    AMBIGUOUS_ASSEMBLY = "ambiguous_assembly"


@dataclass(frozen=True, slots=True)
class WorkspaceGrid:
    """Inclusive Cartesian sampling bounds and counts, expressed in metres."""

    x_min_m: float
    x_max_m: float
    x_count: int
    y_min_m: float
    y_max_m: float
    y_count: int
    z_min_m: float
    z_max_m: float
    z_count: int


@dataclass(frozen=True, slots=True)
class WorkspacePoint:
    """One sampled point, its class, diagnostic reason and optional solved angles."""

    position: CartesianPosition
    classification: WorkspaceClassification
    reason: WorkspaceReason
    angles: JointAngles | None
    singularity_metrics: SingularityMetrics | None
    practically_usable: bool


@dataclass(frozen=True, slots=True)
class WorkspaceSummary:
    """Exact counts for one complete workspace sample."""

    total_count: int
    reachable_count: int
    joint_limited_count: int
    unreachable_count: int
    practically_usable_count: int
    weak_reachable_count: int


@dataclass(frozen=True, slots=True)
class WorkspaceSample:
    """Deterministically ordered points and their aggregate counts."""

    geometry: DeltaGeometry
    assembly_mode: AssemblyMode
    grid: WorkspaceGrid
    points: tuple[WorkspacePoint, ...]
    summary: WorkspaceSummary


def _axis_samples(minimum: float, maximum: float, count: int, axis_name: str) -> tuple[float, ...]:
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise GridValidationError(f"{axis_name} bounds must be finite")
    if minimum > maximum:
        raise GridValidationError(f"{axis_name}_min_m must not exceed {axis_name}_max_m")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise GridValidationError(f"{axis_name}_count must be an integer of at least one")
    if count > 1 and minimum == maximum:
        raise GridValidationError(
            f"zero-width {axis_name} bounds require {axis_name}_count equal to one"
        )
    if count == 1:
        return (minimum / 2.0 + maximum / 2.0,)
    interval = maximum - minimum
    return tuple(minimum + interval * index / (count - 1) for index in range(count))


def grid_positions(grid: WorkspaceGrid) -> tuple[CartesianPosition, ...]:
    """Return grid positions in stable Z/Y/X traversal with X changing fastest."""

    x_values = _axis_samples(grid.x_min_m, grid.x_max_m, grid.x_count, "x")
    y_values = _axis_samples(grid.y_min_m, grid.y_max_m, grid.y_count, "y")
    z_values = _axis_samples(grid.z_min_m, grid.z_max_m, grid.z_count, "z")
    return tuple(
        CartesianPosition(x_m=x_m, y_m=y_m, z_m=z_m)
        for z_m in z_values
        for y_m in y_values
        for x_m in x_values
    )


def _unreachable_result(
    position: CartesianPosition,
    error: UnreachablePositionError
    | DegeneratePositionError
    | AssemblyConstraintError
    | AmbiguousAssemblyError,
) -> WorkspacePoint:
    if isinstance(error, UnreachablePositionError):
        reason = WorkspaceReason.GEOMETRIC_UNREACHABLE
    elif isinstance(error, DegeneratePositionError):
        reason = WorkspaceReason.DEGENERATE_BOUNDARY
    elif isinstance(error, AssemblyConstraintError):
        reason = WorkspaceReason.ASSEMBLY_CONSTRAINT
    else:
        reason = WorkspaceReason.AMBIGUOUS_ASSEMBLY
    return WorkspacePoint(
        position=position,
        classification=WorkspaceClassification.UNREACHABLE,
        reason=reason,
        angles=None,
        singularity_metrics=None,
        practically_usable=False,
    )


def classify_workspace_point(
    geometry: DeltaGeometry,
    position: CartesianPosition,
    assembly_mode: AssemblyMode,
) -> WorkspacePoint:
    """Classify one position while separating actuator limits from link reach."""

    try:
        result = inverse_kinematics(geometry, position, assembly_mode)
    except JointLimitError:
        unrestricted_geometry = replace(
            geometry,
            min_joint_angle_rad=-math.pi,
            max_joint_angle_rad=math.pi,
        )
        try:
            unrestricted_result = inverse_kinematics(
                unrestricted_geometry,
                position,
                assembly_mode,
            )
        except (
            UnreachablePositionError,
            DegeneratePositionError,
            AssemblyConstraintError,
            AmbiguousAssemblyError,
        ) as error:
            return _unreachable_result(position, error)
        return WorkspacePoint(
            position=position,
            classification=WorkspaceClassification.JOINT_LIMITED,
            reason=WorkspaceReason.JOINT_LIMIT,
            angles=unrestricted_result.angles,
            singularity_metrics=differential_kinematics(
                unrestricted_geometry,
                position,
                assembly_mode,
            ).metrics,
            practically_usable=False,
        )
    except (
        UnreachablePositionError,
        DegeneratePositionError,
        AssemblyConstraintError,
        AmbiguousAssemblyError,
    ) as error:
        return _unreachable_result(position, error)
    metrics = differential_kinematics(geometry, position, assembly_mode).metrics
    return WorkspacePoint(
        position=position,
        classification=WorkspaceClassification.REACHABLE,
        reason=WorkspaceReason.REACHABLE,
        angles=result.angles,
        singularity_metrics=metrics,
        practically_usable=metrics.singularity_margin >= PRACTICALLY_USABLE_MARGIN,
    )


def sample_workspace(
    geometry: DeltaGeometry,
    grid: WorkspaceGrid,
    assembly_mode: AssemblyMode,
) -> WorkspaceSample:
    """Classify every point of a finite grid and calculate exact class counts."""

    points = tuple(
        classify_workspace_point(geometry, position, assembly_mode)
        for position in grid_positions(grid)
    )
    reachable_count = sum(
        point.classification is WorkspaceClassification.REACHABLE for point in points
    )
    joint_limited_count = sum(
        point.classification is WorkspaceClassification.JOINT_LIMITED for point in points
    )
    unreachable_count = sum(
        point.classification is WorkspaceClassification.UNREACHABLE for point in points
    )
    practically_usable_count = sum(point.practically_usable for point in points)
    weak_reachable_count = sum(
        point.classification is WorkspaceClassification.REACHABLE
        and not point.practically_usable
        for point in points
    )
    summary = WorkspaceSummary(
        total_count=len(points),
        reachable_count=reachable_count,
        joint_limited_count=joint_limited_count,
        unreachable_count=unreachable_count,
        practically_usable_count=practically_usable_count,
        weak_reachable_count=weak_reachable_count,
    )
    if reachable_count + joint_limited_count + unreachable_count != len(points):
        raise RuntimeError("workspace classification counts do not match grid cardinality")
    return WorkspaceSample(
        geometry=geometry,
        assembly_mode=assembly_mode,
        grid=grid,
        points=points,
        summary=summary,
    )
