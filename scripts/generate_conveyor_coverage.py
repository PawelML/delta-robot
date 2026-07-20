"""Generate deterministic P0 evidence for the 305 x 200 mm conveyor footprint."""

import json
import math
from dataclasses import asdict
from pathlib import Path

from delta_model.conventions import CartesianPosition
from delta_model.conveyor_coverage import evaluate_conveyor_coverage
from delta_model.design_geometry import (
    SELECTED_CONVEYOR_FOOTPRINT,
    SELECTED_GEOMETRY,
    SELECTED_USEFUL_CYLINDER,
)


def coverage_document() -> dict[str, object]:
    """Return the serializable coverage report and reject a stale design."""

    result = evaluate_conveyor_coverage(
        SELECTED_GEOMETRY,
        SELECTED_CONVEYOR_FOOTPRINT,
        SELECTED_USEFUL_CYLINDER,
    )
    if not result.passes:
        raise RuntimeError("selected conveyor footprint does not pass the P0 design reserves")

    def position_document(position: CartesianPosition | None) -> dict[str, float] | None:
        if position is None:
            return None
        return asdict(position)

    return {
        "classification_counts": {
            "joint_limited": result.joint_limited_count,
            "practically_usable": result.practically_usable_count,
            "reachable": result.reachable_count,
            "unreachable": result.unreachable_count,
        },
        "footprint": asdict(SELECTED_CONVEYOR_FOOTPRINT),
        "geometry": asdict(SELECTED_GEOMETRY),
        "result": {
            "contained_in_useful_cylinder": result.contained_in_useful_cylinder,
            "corner_radius_m": result.corner_radius_m,
            "minimum_joint_limit_margin_deg": (
                math.degrees(result.minimum_joint_limit_margin_rad)
                if result.minimum_joint_limit_margin_rad is not None
                else None
            ),
            "minimum_joint_limit_margin_rad": result.minimum_joint_limit_margin_rad,
            "minimum_singularity_margin": result.minimum_singularity_margin,
            "passes": result.passes,
            "radial_reserve_m": result.radial_reserve_m,
            "weakest_joint_position_m": position_document(result.weakest_joint_position),
            "weakest_singularity_position_m": position_document(
                result.weakest_singularity_position
            ),
        },
        "sampling": {**asdict(result.sampling), "point_count": result.sampling.point_count},
        "schema": "delta-robot-p0-conveyor-coverage/v1",
        "thresholds": {
            "joint_limit_reserve_deg": 5.0,
            "singularity_margin": 0.20,
        },
        "units": {"angle": "rad unless suffixed _deg", "length": "m"},
        "useful_cylinder": asdict(SELECTED_USEFUL_CYLINDER),
    }


def main() -> None:
    """Write the stable JSON artifact."""

    output = Path(__file__).resolve().parents[1] / "artifacts/conveyor_coverage.json"
    output.write_text(
        json.dumps(coverage_document(), allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
