import math

import pytest

from delta_model.design_geometry import (
    GEOMETRY_CANDIDATES,
    SELECTED_GEOMETRY,
    SELECTED_USEFUL_CYLINDER,
)
from delta_model.geometry_selection import (
    FINAL_SAMPLING,
    CylinderSampling,
    cylinder_positions,
    evaluate_cylinder,
)


def test_final_cylinder_grid_has_expected_cardinality_and_boundaries() -> None:
    positions = cylinder_positions(0.4, 0.15, -0.35, FINAL_SAMPLING)

    assert len(positions) == 9232
    assert positions[0].z_m == pytest.approx(-0.425, abs=1e-15)
    assert positions[-1].z_m == pytest.approx(-0.275, abs=1e-15)
    assert max(math.hypot(point.x_m, point.y_m) for point in positions) == pytest.approx(
        0.2, abs=1e-15
    )


def test_small_sampling_rejects_a_compact_geometry_at_impossible_depth() -> None:
    sampling = CylinderSampling(z_plane_count=2, radial_level_count=2, azimuth_count=6)

    result = evaluate_cylinder(GEOMETRY_CANDIDATES[0], 0.4, -0.7, sampling)

    assert not result.all_reachable
    assert not result.passes
    assert result.failure is not None


def test_selected_geometry_passes_full_400_by_150_mm_cylinder() -> None:
    selected_candidate = GEOMETRY_CANDIDATES[2]
    assert selected_candidate.geometry == SELECTED_GEOMETRY

    result = evaluate_cylinder(
        selected_candidate,
        SELECTED_USEFUL_CYLINDER.radius_m * 2.0,
        SELECTED_USEFUL_CYLINDER.center_z_m,
        FINAL_SAMPLING,
    )

    assert result.sample_count == 9232
    assert result.evaluated_count == result.sample_count
    assert result.passes
    assert result.minimum_singularity_margin == pytest.approx(0.5713616327636166, abs=1e-12)
    assert math.degrees(result.minimum_joint_limit_margin_rad or 0.0) == pytest.approx(
        11.959644081325294, abs=1e-10
    )
