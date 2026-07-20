"""Generate the deterministic P0 DIY geometry comparison report."""

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import cast

from delta_model.design_geometry import (
    GEOMETRY_CANDIDATES,
    SELECTED_CANDIDATE_ID,
    SELECTED_USEFUL_CYLINDER,
)
from delta_model.geometry_selection import (
    COARSE_SAMPLING,
    DESIGN_SINGULARITY_MARGIN,
    DIAMETERS_M,
    FINAL_SAMPLING,
    JOINT_LIMIT_RESERVE_RAD,
    CandidateScreening,
    CylinderEvaluation,
    screen_candidate,
)


def _geometry_document(screening: CandidateScreening) -> dict[str, float]:
    geometry = screening.candidate.geometry
    return {
        "base_joint_radius_m": geometry.base_joint_radius_m,
        "lower_arm_length_m": geometry.lower_arm_length_m,
        "max_joint_angle_rad": geometry.max_joint_angle_rad,
        "min_joint_angle_rad": geometry.min_joint_angle_rad,
        "platform_joint_radius_m": geometry.platform_joint_radius_m,
        "upper_arm_length_m": geometry.upper_arm_length_m,
    }


def _evaluation_document(evaluation: CylinderEvaluation) -> dict[str, object]:
    weakest = evaluation.weakest_position
    return {
        "all_reachable": evaluation.all_reachable,
        "center_z_m": evaluation.center_z_m,
        "evaluated_count": evaluation.evaluated_count,
        "failure": evaluation.failure,
        "minimum_joint_limit_margin_rad": evaluation.minimum_joint_limit_margin_rad,
        "minimum_singularity_margin": evaluation.minimum_singularity_margin,
        "overall_reserve_ratio": evaluation.overall_reserve_ratio,
        "passes": evaluation.passes,
        "sample_count": evaluation.sample_count,
        "weakest_position_m": (
            [weakest.x_m, weakest.y_m, weakest.z_m] if weakest is not None else None
        ),
    }


def comparison_document() -> dict[str, object]:
    """Run all screenings and serialize the deterministic decision evidence."""

    screenings = tuple(screen_candidate(candidate) for candidate in GEOMETRY_CANDIDATES)
    selected = next(
        screening
        for screening in screenings
        if screening.candidate.candidate_id == SELECTED_CANDIDATE_ID
    )
    selected_diameter = next(
        diameter
        for diameter in selected.diameters
        if math.isclose(diameter.diameter_m, SELECTED_USEFUL_CYLINDER.radius_m * 2.0)
    )
    if not selected_diameter.best_refined.passes:
        raise RuntimeError("configured selected geometry no longer passes its useful cylinder")
    if not math.isclose(
        selected_diameter.best_refined.center_z_m,
        SELECTED_USEFUL_CYLINDER.center_z_m,
        abs_tol=1e-12,
    ):
        raise RuntimeError("configured useful-cylinder Z no longer matches screening result")

    return {
        "candidates": [
            {
                "candidate_id": screening.candidate.candidate_id,
                "diameters": [
                    {
                        "best_coarse": _evaluation_document(diameter.best_coarse),
                        "best_refined": _evaluation_document(diameter.best_refined),
                        "diameter_m": diameter.diameter_m,
                    }
                    for diameter in screening.diameters
                ],
                "geometry": _geometry_document(screening),
                "rationale": screening.candidate.rationale,
            }
            for screening in screenings
        ],
        "limitations": [
            "sampled evidence is not a continuous-volume proof",
            "collisions and physical joint articulation are not modelled",
            "stiffness and dynamic adequacy remain unverified",
            "selection does not authorize purchases",
        ],
        "sampling": {
            "coarse": asdict(COARSE_SAMPLING),
            "coarse_z_step_m": 0.005,
            "final": asdict(FINAL_SAMPLING),
            "refined_z_step_m": 0.001,
        },
        "schema": "delta-robot-p0-geometry-comparison/v1",
        "selected_candidate_id": SELECTED_CANDIDATE_ID,
        "selected_diameter_m": selected_diameter.diameter_m,
        "selected_evidence": _evaluation_document(selected_diameter.best_refined),
        "selection_rationale": (
            "only candidate passing the preferred 0.400 m diameter with both reserves"
        ),
        "thresholds": {
            "cylinder_height_m": 0.150,
            "diameters_m": list(DIAMETERS_M),
            "joint_limit_reserve_rad": JOINT_LIMIT_RESERVE_RAD,
            "singularity_margin": DESIGN_SINGULARITY_MARGIN,
        },
        "units": {"angle": "rad", "length": "m"},
    }


def main() -> None:
    """Write comparison evidence and fail when its declared selection is stale."""

    document = comparison_document()
    output = Path(__file__).resolve().parents[1] / "artifacts/geometry_comparison.json"
    output.write_text(
        json.dumps(document, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    selected = cast(dict[str, object], document["selected_evidence"])
    print(
        f"selected={document['selected_candidate_id']} "
        f"diameter={document['selected_diameter_m']} "
        f"z={selected['center_z_m']} reserve={selected['overall_reserve_ratio']}"
    )


if __name__ == "__main__":
    main()
