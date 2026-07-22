"""Time-parametrized 25-305-25 P0 pick-and-place trajectory."""

import math
from dataclasses import dataclass
from enum import StrEnum

from delta_model.conventions import AssemblyMode, CartesianPosition, JointAngles
from delta_model.design_geometry import SELECTED_GEOMETRY, SELECTED_USEFUL_CYLINDER
from delta_model.differential_kinematics import (
    PRACTICALLY_USABLE_MARGIN,
    CartesianAcceleration,
    CartesianVelocity,
    DifferentialKinematicsResult,
    JointAccelerations,
    JointRates,
    differential_kinematics,
    joint_accelerations_for_cartesian_motion,
    joint_rates_for_cartesian_velocity,
)
from delta_model.geometry import DeltaGeometry
from delta_model.geometry_selection import JOINT_LIMIT_RESERVE_RAD

TRAJECTORY_SAMPLE_PERIOD_S = 0.001


class TrajectoryValidationError(ValueError):
    """Raised when the requested trajectory violates its accepted P0 contract."""


class SegmentKind(StrEnum):
    """Human-readable phase names for one complete round trip."""

    SOURCE_DWELL = "source_dwell"
    OUTBOUND_LIFT = "outbound_lift"
    OUTBOUND_TRANSFER = "outbound_transfer"
    OUTBOUND_LOWER = "outbound_lower"
    DESTINATION_DWELL = "destination_dwell"
    RETURN_LIFT = "return_lift"
    RETURN_TRANSFER = "return_transfer"
    RETURN_LOWER = "return_lower"


@dataclass(frozen=True, slots=True)
class TrajectorySegment:
    """One C2 quintic or stationary segment."""

    kind: SegmentKind
    duration_s: float
    start: CartesianPosition
    end: CartesianPosition


@dataclass(frozen=True, slots=True)
class CartesianMotionState:
    """Exact Cartesian state produced by one segment's analytic motion law."""

    position: CartesianPosition
    velocity: CartesianVelocity
    acceleration: CartesianAcceleration


@dataclass(frozen=True, slots=True)
class TrajectorySample:
    """Complete authoritative model state at one time sample."""

    time_s: float
    segment: SegmentKind
    cartesian: CartesianMotionState
    differential: DifferentialKinematicsResult
    joint_rates: JointRates
    joint_accelerations: JointAccelerations
    joint_limit_margin_rad: float

    @property
    def angles(self) -> JointAngles:
        return self.differential.inverse_result.angles


@dataclass(frozen=True, slots=True)
class TrajectorySummary:
    """Extrema over the finite 1 ms trajectory sample."""

    minimum_singularity_margin: float
    minimum_joint_limit_margin_rad: float
    maximum_cartesian_speed_m_s: float
    maximum_cartesian_acceleration_m_s2: float
    maximum_abs_joint_rates_rad_s: tuple[float, float, float]
    maximum_abs_joint_accelerations_rad_s2: tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class Trajectory:
    """One complete sampled cycle and its provenance."""

    geometry: DeltaGeometry
    assembly_mode: AssemblyMode
    sample_period_s: float
    segments: tuple[TrajectorySegment, ...]
    samples: tuple[TrajectorySample, ...]
    summary: TrajectorySummary

    @property
    def duration_s(self) -> float:
        return sum(segment.duration_s for segment in self.segments)


def trajectory_segments(cycle_time_scale: float = 1.0) -> tuple[TrajectorySegment, ...]:
    """Return the 25-305-25 schedule with uniformly scaled segment times."""

    if not math.isfinite(cycle_time_scale) or cycle_time_scale <= 0.0:
        raise TrajectoryValidationError("cycle time scale must be finite and positive")

    low_z_m = SELECTED_USEFUL_CYLINDER.center_z_m - 0.050
    transfer_z_m = low_z_m + 0.025
    source_low = CartesianPosition(-0.1525, 0.0, low_z_m)
    source_transfer = CartesianPosition(-0.1525, 0.0, transfer_z_m)
    destination_low = CartesianPosition(0.1525, 0.0, low_z_m)
    destination_transfer = CartesianPosition(0.1525, 0.0, transfer_z_m)
    return (
        TrajectorySegment(
            SegmentKind.SOURCE_DWELL,
            0.050 * cycle_time_scale,
            source_low,
            source_low,
        ),
        TrajectorySegment(
            SegmentKind.OUTBOUND_LIFT,
            0.100 * cycle_time_scale,
            source_low,
            source_transfer,
        ),
        TrajectorySegment(
            SegmentKind.OUTBOUND_TRANSFER,
            0.250 * cycle_time_scale,
            source_transfer,
            destination_transfer,
        ),
        TrajectorySegment(
            SegmentKind.OUTBOUND_LOWER,
            0.100 * cycle_time_scale,
            destination_transfer,
            destination_low,
        ),
        TrajectorySegment(
            SegmentKind.DESTINATION_DWELL,
            0.050 * cycle_time_scale,
            destination_low,
            destination_low,
        ),
        TrajectorySegment(
            SegmentKind.RETURN_LIFT,
            0.100 * cycle_time_scale,
            destination_low,
            destination_transfer,
        ),
        TrajectorySegment(
            SegmentKind.RETURN_TRANSFER,
            0.250 * cycle_time_scale,
            destination_transfer,
            source_transfer,
        ),
        TrajectorySegment(
            SegmentKind.RETURN_LOWER,
            0.100 * cycle_time_scale,
            source_transfer,
            source_low,
        ),
    )


def _vector(position: CartesianPosition) -> tuple[float, float, float]:
    return (position.x_m, position.y_m, position.z_m)


def segment_state(segment: TrajectorySegment, local_time_s: float) -> CartesianMotionState:
    """Evaluate one segment's analytic position, velocity and acceleration."""

    if not math.isfinite(local_time_s) or not 0.0 <= local_time_s <= segment.duration_s:
        raise TrajectoryValidationError("local segment time must lie inside its duration")
    normalized_time = local_time_s / segment.duration_s
    tau = min(1.0, max(0.0, normalized_time))
    blend = 10.0 * tau**3 - 15.0 * tau**4 + 6.0 * tau**5
    blend_rate = (30.0 * tau**2 - 60.0 * tau**3 + 30.0 * tau**4) / segment.duration_s
    blend_acceleration = (
        60.0 * tau - 180.0 * tau**2 + 120.0 * tau**3
    ) / segment.duration_s**2
    start = _vector(segment.start)
    delta = tuple(
        end - beginning
        for beginning, end in zip(start, _vector(segment.end), strict=True)
    )
    position = tuple(start[index] + blend * delta[index] for index in range(3))
    velocity = tuple(blend_rate * component for component in delta)
    acceleration = tuple(blend_acceleration * component for component in delta)
    return CartesianMotionState(
        position=CartesianPosition(*position),
        velocity=CartesianVelocity(*velocity),
        acceleration=CartesianAcceleration(*acceleration),
    )


def trajectory_cartesian_state(
    segments: tuple[TrajectorySegment, ...],
    time_s: float,
) -> tuple[SegmentKind, CartesianMotionState]:
    """Evaluate the scheduled segment at one absolute cycle time."""

    duration_s = sum(segment.duration_s for segment in segments)
    if not math.isfinite(time_s) or not 0.0 <= time_s <= duration_s:
        raise TrajectoryValidationError("trajectory time must lie inside the cycle")
    elapsed_s = 0.0
    for index, segment in enumerate(segments):
        segment_end_s = elapsed_s + segment.duration_s
        if time_s <= segment_end_s + 1e-15 or index == len(segments) - 1:
            local_time_s = min(segment.duration_s, max(0.0, time_s - elapsed_s))
            return segment.kind, segment_state(segment, local_time_s)
        elapsed_s = segment_end_s
    raise RuntimeError("trajectory segment selection failed")


def _joint_limit_margin(geometry: DeltaGeometry, angles: JointAngles) -> float:
    return min(
        min(angle - geometry.min_joint_angle_rad, geometry.max_joint_angle_rad - angle)
        for angle in (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad)
    )


def _sample(
    geometry: DeltaGeometry,
    segments: tuple[TrajectorySegment, ...],
    time_s: float,
) -> TrajectorySample:
    segment, cartesian = trajectory_cartesian_state(segments, time_s)
    differential = differential_kinematics(
        geometry,
        cartesian.position,
        AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
    )
    joint_margin = _joint_limit_margin(geometry, differential.inverse_result.angles)
    if differential.metrics.singularity_margin < PRACTICALLY_USABLE_MARGIN:
        raise TrajectoryValidationError(
            f"sample at {time_s} s is below the singularity-margin requirement"
        )
    if joint_margin < JOINT_LIMIT_RESERVE_RAD:
        raise TrajectoryValidationError(
            f"sample at {time_s} s is below the joint-limit reserve requirement"
        )
    rates = joint_rates_for_cartesian_velocity(differential, cartesian.velocity)
    accelerations = joint_accelerations_for_cartesian_motion(
        differential,
        cartesian.velocity,
        cartesian.acceleration,
        rates,
    )
    return TrajectorySample(
        time_s=time_s,
        segment=segment,
        cartesian=cartesian,
        differential=differential,
        joint_rates=rates,
        joint_accelerations=accelerations,
        joint_limit_margin_rad=joint_margin,
    )


def _summary(samples: tuple[TrajectorySample, ...]) -> TrajectorySummary:
    rate_rows = tuple(
        (
            sample.joint_rates.theta_1_rad_s,
            sample.joint_rates.theta_2_rad_s,
            sample.joint_rates.theta_3_rad_s,
        )
        for sample in samples
    )
    acceleration_rows = tuple(
        (
            sample.joint_accelerations.theta_1_rad_s2,
            sample.joint_accelerations.theta_2_rad_s2,
            sample.joint_accelerations.theta_3_rad_s2,
        )
        for sample in samples
    )
    maximum_rates = tuple(max(abs(row[index]) for row in rate_rows) for index in range(3))
    maximum_accelerations = tuple(
        max(abs(row[index]) for row in acceleration_rows) for index in range(3)
    )
    return TrajectorySummary(
        minimum_singularity_margin=min(
            sample.differential.metrics.singularity_margin for sample in samples
        ),
        minimum_joint_limit_margin_rad=min(sample.joint_limit_margin_rad for sample in samples),
        maximum_cartesian_speed_m_s=max(
            math.sqrt(
                sample.cartesian.velocity.x_m_s**2
                + sample.cartesian.velocity.y_m_s**2
                + sample.cartesian.velocity.z_m_s**2
            )
            for sample in samples
        ),
        maximum_cartesian_acceleration_m_s2=max(
            math.sqrt(
                sample.cartesian.acceleration.x_m_s2**2
                + sample.cartesian.acceleration.y_m_s2**2
                + sample.cartesian.acceleration.z_m_s2**2
            )
            for sample in samples
        ),
        maximum_abs_joint_rates_rad_s=(
            maximum_rates[0],
            maximum_rates[1],
            maximum_rates[2],
        ),
        maximum_abs_joint_accelerations_rad_s2=(
            maximum_accelerations[0],
            maximum_accelerations[1],
            maximum_accelerations[2],
        ),
    )


def generate_trajectory(
    geometry: DeltaGeometry = SELECTED_GEOMETRY,
    sample_period_s: float = TRAJECTORY_SAMPLE_PERIOD_S,
    cycle_time_scale: float = 1.0,
) -> Trajectory:
    """Generate the accepted path with an optional uniform time scale."""

    if not math.isfinite(sample_period_s) or sample_period_s <= 0.0:
        raise TrajectoryValidationError("sample period must be finite and positive")
    segments = trajectory_segments(cycle_time_scale)
    duration_s = sum(segment.duration_s for segment in segments)
    interval_count = round(duration_s / sample_period_s)
    if not math.isclose(interval_count * sample_period_s, duration_s, abs_tol=1e-15):
        raise TrajectoryValidationError("sample period must divide the cycle duration exactly")
    samples = tuple(
        _sample(geometry, segments, index * sample_period_s)
        for index in range(interval_count + 1)
    )
    return Trajectory(
        geometry=geometry,
        assembly_mode=AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
        sample_period_s=sample_period_s,
        segments=segments,
        samples=samples,
        summary=_summary(samples),
    )
