import json
import math
from pathlib import Path
from typing import cast

import pytest

from delta_model import AssemblyMode, CartesianPosition, UnreachablePositionError
from delta_model.reference_artifacts import (
    REFERENCE_SOURCE_LABEL,
    generate_reference_artifacts,
)
from delta_model.visualizer_export import (
    POSE_SCHEMA,
    WORKSPACE_SCHEMA,
    pose_document,
    serialize_json_document,
    workspace_document,
    write_json_document,
)
from delta_model.williams import WILLIAMS_GEOMETRY
from delta_model.workspace import WorkspaceGrid, sample_workspace

ASSEMBLY_MODE = AssemblyMode.KNEE_OUT_PLATFORM_BELOW
SOURCE_LABEL = "unit_test_williams_fixture"


def _small_sample_grid() -> WorkspaceGrid:
    return WorkspaceGrid(
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


def _coordinates(value: object) -> tuple[float, float, float]:
    coordinates = cast(list[float], value)
    return (coordinates[0], coordinates[1], coordinates[2])


def test_workspace_document_has_versioned_units_geometry_counts_and_points() -> None:
    sample = sample_workspace(WILLIAMS_GEOMETRY, _small_sample_grid(), ASSEMBLY_MODE)

    document = workspace_document(
        sample,
        source_label=SOURCE_LABEL,
    )

    assert document["schema"] == WORKSPACE_SCHEMA
    assert document["source"] == SOURCE_LABEL
    assert document["units"] == {"angle": "rad", "length": "m"}
    geometry = cast(dict[str, float], document["geometry"])
    assert geometry["upper_arm_length_m"] == WILLIAMS_GEOMETRY.upper_arm_length_m
    summary = cast(dict[str, int], document["summary"])
    points = cast(list[dict[str, object]], document["points"])
    assert summary["total"] == 8
    assert len(points) == summary["total"]
    assert set(points[0]) == {"classification", "position_m", "reason"}


def test_pose_document_contains_authoritative_ik_points_and_closes_links() -> None:
    requested = CartesianPosition(x_m=0.0, y_m=0.0, z_m=-0.9)

    document = pose_document(
        WILLIAMS_GEOMETRY,
        requested,
        ASSEMBLY_MODE,
        source_label=SOURCE_LABEL,
    )

    assert document["schema"] == POSE_SCHEMA
    assert document["classification"] == "reachable"
    pose = cast(dict[str, object], document["pose"])
    assert _coordinates(pose["platform_center_m"]) == (0.0, 0.0, -0.9)
    angles = cast(list[float], pose["joint_angles_rad"])
    assert len(angles) == 3
    assert all(math.isfinite(angle) for angle in angles)

    arms = cast(list[dict[str, object]], pose["arms"])
    assert len(arms) == 3
    for arm in arms:
        shoulder = _coordinates(arm["shoulder_m"])
        knee = _coordinates(arm["knee_m"])
        attachment = _coordinates(arm["platform_attachment_m"])
        assert math.dist(shoulder, knee) == pytest.approx(
            WILLIAMS_GEOMETRY.upper_arm_length_m,
            abs=1e-12,
        )
        assert math.dist(knee, attachment) == pytest.approx(
            WILLIAMS_GEOMETRY.lower_arm_length_m,
            abs=1e-12,
        )


def test_json_serialization_is_strict_stable_and_newline_terminated(tmp_path: Path) -> None:
    document: dict[str, object] = {"z": [3, 2, 1], "a": {"finite": 1.0}}
    first = serialize_json_document(document)
    second = serialize_json_document(document)

    assert first == second
    assert first.endswith("\n")
    assert first.index('"a"') < first.index('"z"')

    output_path = tmp_path / "nested" / "document.json"
    write_json_document(output_path, document)
    assert output_path.read_text(encoding="utf-8") == first
    assert json.loads(first) == document


def test_json_serialization_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError, match="Out of range float values"):
        serialize_json_document({"invalid": math.nan})


def test_unreachable_pose_does_not_produce_a_partial_document() -> None:
    with pytest.raises(UnreachablePositionError):
        pose_document(
            WILLIAMS_GEOMETRY,
            CartesianPosition(x_m=10.0, y_m=0.0, z_m=-0.9),
            ASSEMBLY_MODE,
            source_label=SOURCE_LABEL,
        )


def test_reference_artifacts_regenerate_without_a_diff(tmp_path: Path) -> None:
    generated_workspace, generated_pose = generate_reference_artifacts(tmp_path / "first")
    second_workspace, second_pose = generate_reference_artifacts(tmp_path / "second")
    repository_artifacts = Path(__file__).resolve().parents[1] / "artifacts"

    assert generated_workspace.read_bytes() == second_workspace.read_bytes()
    assert generated_pose.read_bytes() == second_pose.read_bytes()
    assert generated_workspace.read_bytes() == (
        repository_artifacts / "workspace.json"
    ).read_bytes()
    assert generated_pose.read_bytes() == (repository_artifacts / "pose.json").read_bytes()

    workspace = cast(
        dict[str, object],
        json.loads(generated_workspace.read_text(encoding="utf-8")),
    )
    assert workspace["source"] == REFERENCE_SOURCE_LABEL
    assert workspace["summary"] == {
        "joint_limited": 3262,
        "reachable": 4491,
        "total": 9261,
        "unreachable": 1508,
    }
