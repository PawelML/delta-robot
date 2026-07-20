"""Reproducible selected-geometry artifacts for P0 visualization."""

from pathlib import Path

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.design_geometry import (
    SELECTED_GEOMETRY,
    SELECTED_SOURCE_LABEL,
    SELECTED_USEFUL_CYLINDER,
)
from delta_model.visualizer_export import (
    pose_document,
    workspace_document,
    write_json_document,
)
from delta_model.workspace import WorkspaceGrid, sample_workspace

P0_GRID = WorkspaceGrid(
    x_min_m=-0.35,
    x_max_m=0.35,
    x_count=31,
    y_min_m=-0.35,
    y_max_m=0.35,
    y_count=31,
    z_min_m=-0.60,
    z_max_m=-0.15,
    z_count=25,
)
P0_POSE = CartesianPosition(
    x_m=0.0,
    y_m=0.0,
    z_m=SELECTED_USEFUL_CYLINDER.center_z_m,
)
ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW


def generate_p0_artifacts(output_directory: Path) -> tuple[Path, Path]:
    """Generate the selected DIY workspace map and one complete pose."""

    workspace_sample = sample_workspace(SELECTED_GEOMETRY, P0_GRID, ASSEMBLY_MODE)
    workspace_path = output_directory / "workspace.json"
    pose_path = output_directory / "pose.json"
    write_json_document(
        workspace_path,
        workspace_document(
            workspace_sample,
            source_label=SELECTED_SOURCE_LABEL,
        ),
    )
    write_json_document(
        pose_path,
        pose_document(
            SELECTED_GEOMETRY,
            P0_POSE,
            ASSEMBLY_MODE,
            source_label=SELECTED_SOURCE_LABEL,
        ),
    )
    return workspace_path, pose_path
