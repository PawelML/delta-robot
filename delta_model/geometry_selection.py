"""Deterministic sampled screening of candidate DIY delta geometries."""

import math
from dataclasses import dataclass

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.design_geometry import GeometryCandidate
from delta_model.differential_kinematics import differential_kinematics
from delta_model.errors import KinematicsError

DESIGN_SINGULARITY_MARGIN = 0.20
JOINT_LIMIT_RESERVE_RAD = math.radians(5.0)
CYLINDER_HEIGHT_M = 0.150
DIAMETERS_M = (0.400, 0.375, 0.350)
COARSE_Z_CENTERS_M = tuple(-value / 1000.0 for value in range(250, 551, 5))


@dataclass(frozen=True, slots=True)
class CylinderSampling:
    """Finite solid-cylinder lattice definition."""

    z_plane_count: int
    radial_level_count: int
    azimuth_count: int

    @property
    def point_count(self) -> int:
        return self.z_plane_count * (1 + (self.radial_level_count - 1) * self.azimuth_count)


COARSE_SAMPLING = CylinderSampling(z_plane_count=7, radial_level_count=5, azimuth_count=24)
FINAL_SAMPLING = CylinderSampling(z_plane_count=16, radial_level_count=9, azimuth_count=72)


@dataclass(frozen=True, slots=True)
class CylinderEvaluation:
    """Worst sampled margins for one fixed cylinder placement."""

    center_z_m: float
    diameter_m: float
    sample_count: int
    evaluated_count: int
    all_reachable: bool
    passes: bool
    minimum_singularity_margin: float | None
    minimum_joint_limit_margin_rad: float | None
    overall_reserve_ratio: float | None
    weakest_position: CartesianPosition | None
    failure: str | None


@dataclass(frozen=True, slots=True)
class DiameterScreening:
    """Coarse and refined best placements for one candidate diameter."""

    diameter_m: float
    best_coarse: CylinderEvaluation
    best_refined: CylinderEvaluation


@dataclass(frozen=True, slots=True)
class CandidateScreening:
    """All requested diameters evaluated for one geometry candidate."""

    candidate: GeometryCandidate
    diameters: tuple[DiameterScreening, ...]


def cylinder_positions(
    diameter_m: float,
    height_m: float,
    center_z_m: float,
    sampling: CylinderSampling,
) -> tuple[CartesianPosition, ...]:
    """Generate a deterministic solid-cylinder lattice including its boundary."""

    radius_m = diameter_m / 2.0
    positions: list[CartesianPosition] = []
    for z_index in range(sampling.z_plane_count):
        z_m = center_z_m - height_m / 2.0 + height_m * z_index / (
            sampling.z_plane_count - 1
        )
        for radial_index in range(sampling.radial_level_count):
            radial_m = radius_m * radial_index / (sampling.radial_level_count - 1)
            count = 1 if radial_index == 0 else sampling.azimuth_count
            for azimuth_index in range(count):
                azimuth_rad = 2.0 * math.pi * azimuth_index / count
                positions.append(
                    CartesianPosition(
                        x_m=radial_m * math.cos(azimuth_rad),
                        y_m=radial_m * math.sin(azimuth_rad),
                        z_m=z_m,
                    )
                )
    return tuple(positions)


def evaluate_cylinder(
    candidate: GeometryCandidate,
    diameter_m: float,
    center_z_m: float,
    sampling: CylinderSampling,
) -> CylinderEvaluation:
    """Evaluate every sample unless an IK failure makes the placement invalid."""

    geometry = candidate.geometry
    positions = cylinder_positions(diameter_m, CYLINDER_HEIGHT_M, center_z_m, sampling)
    minimum_singularity = math.inf
    minimum_joint = math.inf
    weakest_position: CartesianPosition | None = None
    for index, position in enumerate(positions):
        try:
            result = differential_kinematics(
                geometry,
                position,
                AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
            )
        except KinematicsError as error:
            return CylinderEvaluation(
                center_z_m=center_z_m,
                diameter_m=diameter_m,
                sample_count=len(positions),
                evaluated_count=index + 1,
                all_reachable=False,
                passes=False,
                minimum_singularity_margin=(
                    minimum_singularity if math.isfinite(minimum_singularity) else None
                ),
                minimum_joint_limit_margin_rad=(
                    minimum_joint if math.isfinite(minimum_joint) else None
                ),
                overall_reserve_ratio=None,
                weakest_position=weakest_position,
                failure=type(error).__name__,
            )
        angles = result.inverse_result.angles
        angle_values = (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad)
        joint_margin = min(
            min(
                angle - geometry.min_joint_angle_rad,
                geometry.max_joint_angle_rad - angle,
            )
            for angle in angle_values
        )
        singularity_margin = result.metrics.singularity_margin
        normalized = min(
            singularity_margin / DESIGN_SINGULARITY_MARGIN,
            joint_margin / JOINT_LIMIT_RESERVE_RAD,
        )
        previous_normalized = min(
            minimum_singularity / DESIGN_SINGULARITY_MARGIN,
            minimum_joint / JOINT_LIMIT_RESERVE_RAD,
        )
        if weakest_position is None or normalized < previous_normalized:
            weakest_position = position
        minimum_singularity = min(minimum_singularity, singularity_margin)
        minimum_joint = min(minimum_joint, joint_margin)

    overall = min(
        minimum_singularity / DESIGN_SINGULARITY_MARGIN,
        minimum_joint / JOINT_LIMIT_RESERVE_RAD,
    )
    return CylinderEvaluation(
        center_z_m=center_z_m,
        diameter_m=diameter_m,
        sample_count=len(positions),
        evaluated_count=len(positions),
        all_reachable=True,
        passes=overall >= 1.0,
        minimum_singularity_margin=minimum_singularity,
        minimum_joint_limit_margin_rad=minimum_joint,
        overall_reserve_ratio=overall,
        weakest_position=weakest_position,
        failure=None if overall >= 1.0 else "insufficient_design_reserve",
    )


def _evaluation_score(evaluation: CylinderEvaluation) -> tuple[float, int]:
    return (
        evaluation.overall_reserve_ratio
        if evaluation.overall_reserve_ratio is not None
        else -1.0,
        evaluation.evaluated_count,
    )


def screen_diameter(candidate: GeometryCandidate, diameter_m: float) -> DiameterScreening:
    """Search Z coarsely, then fully validate the local 1 mm neighborhood."""

    coarse_evaluations = tuple(
        evaluate_cylinder(candidate, diameter_m, center_z_m, COARSE_SAMPLING)
        for center_z_m in COARSE_Z_CENTERS_M
    )
    best_coarse = max(coarse_evaluations, key=_evaluation_score)
    refined_centers = tuple(best_coarse.center_z_m + offset / 1000.0 for offset in range(-5, 6))
    refined_evaluations = tuple(
        evaluate_cylinder(candidate, diameter_m, center_z_m, FINAL_SAMPLING)
        for center_z_m in refined_centers
    )
    return DiameterScreening(
        diameter_m=diameter_m,
        best_coarse=best_coarse,
        best_refined=max(refined_evaluations, key=_evaluation_score),
    )


def screen_candidate(candidate: GeometryCandidate) -> CandidateScreening:
    """Evaluate every HLD diameter for one candidate."""

    return CandidateScreening(
        candidate=candidate,
        diameters=tuple(screen_diameter(candidate, diameter) for diameter in DIAMETERS_M),
    )
