import math
from dataclasses import replace

import pytest

from delta_model import AssemblyMode, CartesianPosition, InvalidPositionError
from delta_model.williams import WILLIAMS_GEOMETRY
from delta_model.workspace import (
    GridValidationError,
    WorkspaceClassification,
    WorkspaceGrid,
    WorkspaceReason,
    classify_workspace_point,
    grid_positions,
    sample_workspace,
)

ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW


def test_known_williams_point_is_reachable_with_finite_angles() -> None:
    result = classify_workspace_point(
        WILLIAMS_GEOMETRY,
        CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.9),
        ASSEMBLY_MODE,
    )

    assert result.classification is WorkspaceClassification.REACHABLE
    assert result.reason is WorkspaceReason.REACHABLE
    assert result.angles is not None
    assert all(
        math.isfinite(angle)
        for angle in (
            result.angles.theta_1_rad,
            result.angles.theta_2_rad,
            result.angles.theta_3_rad,
        )
    )


def test_geometrically_reachable_point_outside_configured_limits_is_joint_limited() -> None:
    narrow_limits = replace(
        WILLIAMS_GEOMETRY,
        min_joint_angle_rad=math.radians(-5.0),
        max_joint_angle_rad=math.radians(5.0),
    )

    result = classify_workspace_point(
        narrow_limits,
        CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.9),
        ASSEMBLY_MODE,
    )

    assert result.classification is WorkspaceClassification.JOINT_LIMITED
    assert result.reason is WorkspaceReason.JOINT_LIMIT
    assert result.angles is not None


@pytest.mark.parametrize(
    ("position", "expected_reason"),
    [
        (
            CartesianPosition(x_m=10.0, y_m=0.0, z_m=-0.9),
            WorkspaceReason.GEOMETRIC_UNREACHABLE,
        ),
        (
            CartesianPosition(x_m=0.0, y_m=0.0, z_m=0.9),
            WorkspaceReason.ASSEMBLY_CONSTRAINT,
        ),
    ],
)
def test_unreachable_points_preserve_diagnostic_reason(
    position: CartesianPosition,
    expected_reason: WorkspaceReason,
) -> None:
    result = classify_workspace_point(WILLIAMS_GEOMETRY, position, ASSEMBLY_MODE)

    assert result.classification is WorkspaceClassification.UNREACHABLE
    assert result.reason is expected_reason
    assert result.angles is None


def test_non_finite_point_remains_a_caller_error() -> None:
    with pytest.raises(InvalidPositionError, match="must be finite"):
        classify_workspace_point(
            WILLIAMS_GEOMETRY,
            CartesianPosition(x_m=math.nan, y_m=0.0, z_m=-0.9),
            ASSEMBLY_MODE,
        )


@pytest.mark.parametrize(
    "invalid_grid",
    [
        WorkspaceGrid(-math.inf, 1.0, 2, -1.0, 1.0, 2, -2.0, -1.0, 2),
        WorkspaceGrid(1.0, -1.0, 2, -1.0, 1.0, 2, -2.0, -1.0, 2),
        WorkspaceGrid(-1.0, 1.0, 0, -1.0, 1.0, 2, -2.0, -1.0, 2),
        WorkspaceGrid(-1.0, 1.0, True, -1.0, 1.0, 2, -2.0, -1.0, 2),
        WorkspaceGrid(0.0, 0.0, 2, -1.0, 1.0, 2, -2.0, -1.0, 2),
    ],
)
def test_invalid_grid_is_rejected(invalid_grid: WorkspaceGrid) -> None:
    with pytest.raises(GridValidationError):
        grid_positions(invalid_grid)


def test_grid_includes_endpoints_uses_midpoint_and_changes_x_fastest() -> None:
    grid = WorkspaceGrid(
        x_min_m=-1.0,
        x_max_m=1.0,
        x_count=3,
        y_min_m=2.0,
        y_max_m=4.0,
        y_count=1,
        z_min_m=-2.0,
        z_max_m=-1.0,
        z_count=2,
    )

    assert grid_positions(grid) == (
        CartesianPosition(x_m=-1.0, y_m=3.0, z_m=-2.0),
        CartesianPosition(x_m=0.0, y_m=3.0, z_m=-2.0),
        CartesianPosition(x_m=1.0, y_m=3.0, z_m=-2.0),
        CartesianPosition(x_m=-1.0, y_m=3.0, z_m=-1.0),
        CartesianPosition(x_m=0.0, y_m=3.0, z_m=-1.0),
        CartesianPosition(x_m=1.0, y_m=3.0, z_m=-1.0),
    )


def test_sample_summary_has_exact_cardinality_and_counts() -> None:
    grid = WorkspaceGrid(
        x_min_m=-0.05,
        x_max_m=0.05,
        x_count=2,
        y_min_m=-0.05,
        y_max_m=0.05,
        y_count=2,
        z_min_m=-1.0,
        z_max_m=-0.9,
        z_count=2,
    )

    sample = sample_workspace(WILLIAMS_GEOMETRY, grid, ASSEMBLY_MODE)

    assert sample.geometry == WILLIAMS_GEOMETRY
    assert sample.assembly_mode is ASSEMBLY_MODE
    assert len(sample.points) == 8
    assert sample.summary.total_count == 8
    assert (
        sample.summary.reachable_count
        + sample.summary.joint_limited_count
        + sample.summary.unreachable_count
        == sample.summary.total_count
    )
    assert sample.summary.reachable_count == 8
