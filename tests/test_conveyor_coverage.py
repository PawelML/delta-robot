import math

import pytest

from delta_model.conveyor_coverage import (
    DEFAULT_CONVEYOR_SAMPLING,
    evaluate_conveyor_coverage,
    footprint_corner_radius,
)
from delta_model.design_geometry import (
    SELECTED_CONVEYOR_FOOTPRINT,
    SELECTED_GEOMETRY,
    SELECTED_USEFUL_CYLINDER,
    ConveyorFootprint,
)


def test_selected_305_by_200_footprint_has_analytical_radial_reserve() -> None:
    corner_radius = footprint_corner_radius(SELECTED_CONVEYOR_FOOTPRINT)

    assert corner_radius == pytest.approx(math.hypot(0.1525, 0.1000), abs=1e-15)
    assert SELECTED_USEFUL_CYLINDER.radius_m - corner_radius == pytest.approx(
        0.01763703775163117, abs=1e-15
    )


def test_selected_footprint_passes_full_height_sampling() -> None:
    result = evaluate_conveyor_coverage(
        SELECTED_GEOMETRY,
        SELECTED_CONVEYOR_FOOTPRINT,
        SELECTED_USEFUL_CYLINDER,
    )

    assert DEFAULT_CONVEYOR_SAMPLING.point_count == 10_416
    assert result.reachable_count == DEFAULT_CONVEYOR_SAMPLING.point_count
    assert result.joint_limited_count == 0
    assert result.unreachable_count == 0
    assert result.practically_usable_count == DEFAULT_CONVEYOR_SAMPLING.point_count
    assert result.passes
    assert result.minimum_singularity_margin is not None
    assert result.minimum_singularity_margin >= 0.20
    assert result.minimum_joint_limit_margin_rad is not None
    assert result.minimum_joint_limit_margin_rad >= math.radians(5.0)


def test_footprint_outside_useful_cylinder_fails_without_clipping() -> None:
    too_wide = ConveyorFootprint(length_m=0.305, width_m=0.300)

    result = evaluate_conveyor_coverage(
        SELECTED_GEOMETRY,
        too_wide,
        SELECTED_USEFUL_CYLINDER,
    )

    assert not result.contained_in_useful_cylinder
    assert result.radial_reserve_m < 0.0
    assert not result.passes


@pytest.mark.parametrize(
    "footprint",
    [
        ConveyorFootprint(length_m=0.0, width_m=0.2),
        ConveyorFootprint(length_m=0.3, width_m=-0.1),
        ConveyorFootprint(length_m=math.nan, width_m=0.2),
    ],
)
def test_invalid_footprint_is_rejected(footprint: ConveyorFootprint) -> None:
    with pytest.raises(ValueError):
        footprint_corner_radius(footprint)
