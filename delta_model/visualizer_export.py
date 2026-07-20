"""Versioned JSON boundary adapters for the future Three.js visualizer."""

import json
from collections.abc import Mapping
from pathlib import Path

from delta_model.conventions import AssemblyMode, CartesianPoint, CartesianPosition
from delta_model.geometry import DeltaGeometry
from delta_model.inverse_kinematics import inverse_kinematics
from delta_model.trajectory import Trajectory
from delta_model.workspace import WorkspaceSample

WORKSPACE_SCHEMA = "delta-robot-p0-workspace/v2"
POSE_SCHEMA = "delta-robot-p0-pose/v1"
TRAJECTORY_SCHEMA = "delta-robot-p0-trajectory/v1"


def _geometry_document(geometry: DeltaGeometry) -> dict[str, float]:
    return {
        "base_joint_radius_m": geometry.base_joint_radius_m,
        "lower_arm_length_m": geometry.lower_arm_length_m,
        "max_joint_angle_rad": geometry.max_joint_angle_rad,
        "min_joint_angle_rad": geometry.min_joint_angle_rad,
        "platform_joint_radius_m": geometry.platform_joint_radius_m,
        "upper_arm_length_m": geometry.upper_arm_length_m,
    }


def _coordinates(point: CartesianPoint | CartesianPosition) -> list[float]:
    return [point.x_m, point.y_m, point.z_m]


def _common_document(
    schema: str,
    geometry: DeltaGeometry,
    assembly_mode: AssemblyMode,
    source_label: str,
) -> dict[str, object]:
    if not source_label.strip():
        raise ValueError("source_label must not be empty")
    return {
        "assembly_mode": assembly_mode.value,
        "geometry": _geometry_document(geometry),
        "schema": schema,
        "source": source_label,
        "units": {"angle": "rad", "length": "m"},
    }


def workspace_document(
    sample: WorkspaceSample,
    *,
    source_label: str,
) -> dict[str, object]:
    """Convert one complete workspace sample to the v2 visualizer contract."""

    document = _common_document(
        WORKSPACE_SCHEMA,
        sample.geometry,
        sample.assembly_mode,
        source_label,
    )
    grid = sample.grid
    document.update(
        {
            "grid": {
                "bounds_m": {
                    "x": [grid.x_min_m, grid.x_max_m],
                    "y": [grid.y_min_m, grid.y_max_m],
                    "z": [grid.z_min_m, grid.z_max_m],
                },
                "shape": {"x": grid.x_count, "y": grid.y_count, "z": grid.z_count},
                "traversal": "z_y_x__x_fastest",
            },
            "points": [
                {
                    "classification": point.classification.value,
                    "parallel_margin": (
                        point.singularity_metrics.parallel_margin
                        if point.singularity_metrics is not None
                        else None
                    ),
                    "position_m": _coordinates(point.position),
                    "practically_usable": point.practically_usable,
                    "reason": point.reason.value,
                    "serial_margin": (
                        point.singularity_metrics.serial_margin
                        if point.singularity_metrics is not None
                        else None
                    ),
                    "singularity_margin": (
                        point.singularity_metrics.singularity_margin
                        if point.singularity_metrics is not None
                        else None
                    ),
                }
                for point in sample.points
            ],
            "summary": {
                "joint_limited": sample.summary.joint_limited_count,
                "practically_usable": sample.summary.practically_usable_count,
                "reachable": sample.summary.reachable_count,
                "total": sample.summary.total_count,
                "unreachable": sample.summary.unreachable_count,
                "weak_reachable": sample.summary.weak_reachable_count,
            },
        }
    )
    return document


def pose_document(
    geometry: DeltaGeometry,
    position: CartesianPosition,
    assembly_mode: AssemblyMode,
    *,
    source_label: str,
) -> dict[str, object]:
    """Solve and convert one reachable robot pose to the v1 visualizer contract."""

    result = inverse_kinematics(geometry, position, assembly_mode)
    document = _common_document(POSE_SCHEMA, geometry, assembly_mode, source_label)
    document.update(
        {
            "classification": "reachable",
            "pose": {
                "arms": [
                    {
                        "arm_index": arm.arm_index,
                        "knee_m": _coordinates(arm.knee_point),
                        "platform_attachment_m": _coordinates(
                            arm.platform_attachment_point
                        ),
                        "shoulder_m": _coordinates(arm.shoulder_point),
                    }
                    for arm in result.arm_solutions
                ],
                "joint_angles_rad": [
                    result.angles.theta_1_rad,
                    result.angles.theta_2_rad,
                    result.angles.theta_3_rad,
                ],
                "platform_center_m": _coordinates(position),
            },
        }
    )
    return document


def trajectory_document(
    trajectory: Trajectory,
    *,
    source_label: str,
) -> dict[str, object]:
    """Convert an authoritative sampled trajectory to the visualizer v1 contract."""

    document = _common_document(
        TRAJECTORY_SCHEMA,
        trajectory.geometry,
        trajectory.assembly_mode,
        source_label,
    )
    document["units"] = {
        "angle": "rad",
        "angular_acceleration": "rad/s^2",
        "angular_velocity": "rad/s",
        "length": "m",
        "linear_acceleration": "m/s^2",
        "linear_velocity": "m/s",
        "time": "s",
    }
    document.update(
        {
            "cycle": {
                "duration_s": trajectory.duration_s,
                "name": "25-305-25_round_trip_1_hz",
                "sample_count": len(trajectory.samples),
                "sample_period_s": trajectory.sample_period_s,
                "segments": [
                    {
                        "duration_s": segment.duration_s,
                        "end_m": _coordinates(segment.end),
                        "name": segment.kind.value,
                        "start_m": _coordinates(segment.start),
                    }
                    for segment in trajectory.segments
                ],
            },
            "samples": [
                {
                    "arms": [
                        {
                            "arm_index": arm.arm_index,
                            "knee_m": _coordinates(arm.knee_point),
                            "platform_attachment_m": _coordinates(
                                arm.platform_attachment_point
                            ),
                            "shoulder_m": _coordinates(arm.shoulder_point),
                        }
                        for arm in sample.differential.inverse_result.arm_solutions
                    ],
                    "cartesian_acceleration_m_s2": [
                        sample.cartesian.acceleration.x_m_s2,
                        sample.cartesian.acceleration.y_m_s2,
                        sample.cartesian.acceleration.z_m_s2,
                    ],
                    "cartesian_velocity_m_s": [
                        sample.cartesian.velocity.x_m_s,
                        sample.cartesian.velocity.y_m_s,
                        sample.cartesian.velocity.z_m_s,
                    ],
                    "joint_accelerations_rad_s2": [
                        sample.joint_accelerations.theta_1_rad_s2,
                        sample.joint_accelerations.theta_2_rad_s2,
                        sample.joint_accelerations.theta_3_rad_s2,
                    ],
                    "joint_angles_rad": [
                        sample.angles.theta_1_rad,
                        sample.angles.theta_2_rad,
                        sample.angles.theta_3_rad,
                    ],
                    "joint_limit_margin_rad": sample.joint_limit_margin_rad,
                    "joint_rates_rad_s": [
                        sample.joint_rates.theta_1_rad_s,
                        sample.joint_rates.theta_2_rad_s,
                        sample.joint_rates.theta_3_rad_s,
                    ],
                    "parallel_margin": sample.differential.metrics.parallel_margin,
                    "platform_center_m": _coordinates(sample.cartesian.position),
                    "segment": sample.segment.value,
                    "serial_margin": sample.differential.metrics.serial_margin,
                    "singularity_margin": sample.differential.metrics.singularity_margin,
                    "time_s": sample.time_s,
                }
                for sample in trajectory.samples
            ],
            "summary": {
                "maximum_abs_joint_accelerations_rad_s2": list(
                    trajectory.summary.maximum_abs_joint_accelerations_rad_s2
                ),
                "maximum_abs_joint_rates_rad_s": list(
                    trajectory.summary.maximum_abs_joint_rates_rad_s
                ),
                "maximum_cartesian_acceleration_m_s2": (
                    trajectory.summary.maximum_cartesian_acceleration_m_s2
                ),
                "maximum_cartesian_speed_m_s": trajectory.summary.maximum_cartesian_speed_m_s,
                "minimum_joint_limit_margin_rad": (
                    trajectory.summary.minimum_joint_limit_margin_rad
                ),
                "minimum_singularity_margin": trajectory.summary.minimum_singularity_margin,
            },
        }
    )
    return document


def serialize_json_document(document: Mapping[str, object]) -> str:
    """Serialize a document deterministically and reject NaN or infinity."""

    return json.dumps(
        document,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def write_json_document(path: Path, document: Mapping[str, object]) -> None:
    """Create parent directories and write one deterministic UTF-8 JSON document."""

    serialized = serialize_json_document(document)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized, encoding="utf-8")
