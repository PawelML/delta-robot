import math

import pytest

from delta_model.trajectory import (
    TRAJECTORY_SAMPLE_PERIOD_S,
    TrajectorySample,
    generate_trajectory,
    segment_state,
    trajectory_segments,
)


def _angles(trajectory_sample: TrajectorySample) -> tuple[float, float, float]:
    return (
        trajectory_sample.angles.theta_1_rad,
        trajectory_sample.angles.theta_2_rad,
        trajectory_sample.angles.theta_3_rad,
    )


def test_cycle_dimensions_schedule_and_sampling_are_exact() -> None:
    segments = trajectory_segments()
    trajectory = generate_trajectory()

    source_low = segments[0].start
    destination_low = segments[4].start
    assert destination_low.x_m - source_low.x_m == pytest.approx(0.305, abs=1e-15)
    assert segments[1].end.z_m - segments[1].start.z_m == pytest.approx(0.025, abs=1e-15)
    assert sum(segment.duration_s for segment in segments) == pytest.approx(1.0, abs=1e-15)
    assert trajectory.sample_period_s == TRAJECTORY_SAMPLE_PERIOD_S
    assert len(trajectory.samples) == 1001
    assert trajectory.samples[0].time_s == 0.0
    assert trajectory.samples[-1].time_s == 1.0
    assert all(
        later.time_s > earlier.time_s
        for earlier, later in zip(trajectory.samples, trajectory.samples[1:], strict=False)
    )


def test_quintic_segment_has_zero_velocity_and_acceleration_at_both_ends() -> None:
    moving_segment = trajectory_segments()[2]

    start = segment_state(moving_segment, 0.0)
    end = segment_state(moving_segment, moving_segment.duration_s)

    assert start.position == moving_segment.start
    assert end.position == moving_segment.end
    assert start.velocity.x_m_s == pytest.approx(0.0, abs=1e-15)
    assert end.velocity.x_m_s == pytest.approx(0.0, abs=1e-15)
    assert start.acceleration.x_m_s2 == pytest.approx(0.0, abs=1e-15)
    assert end.acceleration.x_m_s2 == pytest.approx(0.0, abs=1e-12)


def test_uniform_time_scaling_preserves_path_and_scales_derivatives() -> None:
    baseline = trajectory_segments()[2]
    slowed = trajectory_segments(cycle_time_scale=2.0)[2]
    baseline_state = segment_state(baseline, 0.4 * baseline.duration_s)
    slowed_state = segment_state(slowed, 0.4 * slowed.duration_s)

    assert slowed_state.position == baseline_state.position
    assert slowed_state.velocity.x_m_s == pytest.approx(
        0.5 * baseline_state.velocity.x_m_s, abs=1e-12
    )
    assert slowed_state.acceleration.x_m_s2 == pytest.approx(
        0.25 * baseline_state.acceleration.x_m_s2, abs=1e-12
    )


def test_invalid_cycle_time_scale_is_rejected() -> None:
    with pytest.raises(ValueError, match="cycle time scale"):
        trajectory_segments(0.0)


def test_complete_cycle_returns_to_identical_model_state() -> None:
    trajectory = generate_trajectory()
    start = trajectory.samples[0]
    end = trajectory.samples[-1]

    assert end.cartesian.position == start.cartesian.position
    assert end.cartesian.velocity == start.cartesian.velocity
    assert end.cartesian.acceleration.x_m_s2 == pytest.approx(
        start.cartesian.acceleration.x_m_s2, abs=1e-12
    )
    assert _angles(end) == pytest.approx(_angles(start), abs=1e-12)
    assert end.joint_rates == start.joint_rates


def test_all_samples_retain_screening_reserves_and_finite_axis_derivatives() -> None:
    trajectory = generate_trajectory()

    assert trajectory.summary.minimum_singularity_margin >= 0.20
    assert trajectory.summary.minimum_joint_limit_margin_rad >= math.radians(5.0)
    for sample in trajectory.samples:
        values = (
            sample.joint_rates.theta_1_rad_s,
            sample.joint_rates.theta_2_rad_s,
            sample.joint_rates.theta_3_rad_s,
            sample.joint_accelerations.theta_1_rad_s2,
            sample.joint_accelerations.theta_2_rad_s2,
            sample.joint_accelerations.theta_3_rad_s2,
        )
        assert all(math.isfinite(value) for value in values)
