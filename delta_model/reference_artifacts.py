"""Reproducible Williams-fixture artifacts for visualizer development."""

import math
from dataclasses import replace
from pathlib import Path

from delta_model.conventions import AssemblyMode
from delta_model.visualizer_export import (
    pose_document,
    workspace_document,
    write_json_document,
)
from delta_model.williams import WILLIAMS_GEOMETRY, WILLIAMS_IK_CASES
from delta_model.workspace import WorkspaceGrid, sample_workspace

REFERENCE_SOURCE_LABEL = "williams_dimensions_plus_demo_joint_limits_not_diy_geometry"
REFERENCE_GEOMETRY = replace(
    WILLIAMS_GEOMETRY,
    min_joint_angle_rad=math.radians(-45.0),
    max_joint_angle_rad=math.radians(45.0),
)
REFERENCE_GRID = WorkspaceGrid(
    x_min_m=-0.45,
    x_max_m=0.45,
    x_count=21,
    y_min_m=-0.45,
    y_max_m=0.45,
    y_count=21,
    z_min_m=-1.45,
    z_max_m=-0.55,
    z_count=21,
)
REFERENCE_POSE = WILLIAMS_IK_CASES[0].position
ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW


def generate_reference_artifacts(output_directory: Path) -> tuple[Path, Path]:
    """Generate the coarse workspace map and one complete pose for Three.js."""

    workspace_sample = sample_workspace(REFERENCE_GEOMETRY, REFERENCE_GRID, ASSEMBLY_MODE)
    workspace_path = output_directory / "workspace.json"
    pose_path = output_directory / "pose.json"
    write_json_document(
        workspace_path,
        workspace_document(
            workspace_sample,
            source_label=REFERENCE_SOURCE_LABEL,
        ),
    )
    write_json_document(
        pose_path,
        pose_document(
            REFERENCE_GEOMETRY,
            REFERENCE_POSE,
            ASSEMBLY_MODE,
            source_label=REFERENCE_SOURCE_LABEL,
        ),
    )
    return workspace_path, pose_path
