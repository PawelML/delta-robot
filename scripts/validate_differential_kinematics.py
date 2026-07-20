"""Produce deterministic finite-difference evidence for differential kinematics."""

import json
import random
from pathlib import Path

import numpy as np

from delta_model.conventions import AssemblyMode, CartesianPosition
from delta_model.differential_kinematics import (
    PRACTICALLY_USABLE_MARGIN,
    CartesianVelocity,
    differential_kinematics,
    joint_rates_for_cartesian_velocity,
)
from delta_model.errors import KinematicsError
from delta_model.williams import WILLIAMS_GEOMETRY

SAMPLE_COUNT = 10_000
RANDOM_SEED = 20260720
FINITE_DIFFERENCE_STEP_S = 1e-6
MAX_CARTESIAN_SPEED_M_S = 0.25


def _angles(position: CartesianPosition) -> np.ndarray:
    result = differential_kinematics(
        WILLIAMS_GEOMETRY,
        position,
        AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
    )
    angles = result.inverse_result.angles
    return np.asarray(
        (angles.theta_1_rad, angles.theta_2_rad, angles.theta_3_rad),
        dtype=np.float64,
    )


def _candidate(rng: random.Random) -> tuple[CartesianPosition, CartesianVelocity]:
    position = CartesianPosition(
        x_m=rng.uniform(-0.45, 0.45),
        y_m=rng.uniform(-0.45, 0.45),
        z_m=rng.uniform(-1.45, -0.55),
    )
    direction = np.asarray(
        (rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0)),
        dtype=np.float64,
    )
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        direction = np.asarray((1.0, 0.0, 0.0), dtype=np.float64)
        norm = 1.0
    speed = rng.uniform(0.01, MAX_CARTESIAN_SPEED_M_S)
    direction *= speed / norm
    return position, CartesianVelocity(
        float(direction[0]),
        float(direction[1]),
        float(direction[2]),
    )


def validation_report() -> dict[str, object]:
    """Compare analytical rates with central-difference IK for 10,000 cases."""

    rng = random.Random(RANDOM_SEED)
    errors: list[float] = []
    residuals: list[float] = []
    attempts = 0
    while len(errors) < SAMPLE_COUNT:
        attempts += 1
        position, velocity = _candidate(rng)
        try:
            result = differential_kinematics(
                WILLIAMS_GEOMETRY,
                position,
                AssemblyMode.KNEE_OUT_PLATFORM_BELOW,
            )
            if result.metrics.singularity_margin < PRACTICALLY_USABLE_MARGIN:
                continue
            rates = joint_rates_for_cartesian_velocity(result, velocity)
            step = FINITE_DIFFERENCE_STEP_S
            before = CartesianPosition(
                position.x_m - step * velocity.x_m_s,
                position.y_m - step * velocity.y_m_s,
                position.z_m - step * velocity.z_m_s,
            )
            after = CartesianPosition(
                position.x_m + step * velocity.x_m_s,
                position.y_m + step * velocity.y_m_s,
                position.z_m + step * velocity.z_m_s,
            )
            finite_difference = (_angles(after) - _angles(before)) / (2.0 * step)
        except KinematicsError:
            continue
        analytical = np.asarray(
            (rates.theta_1_rad_s, rates.theta_2_rad_s, rates.theta_3_rad_s),
            dtype=np.float64,
        )
        error = float(np.max(np.abs(analytical - finite_difference)))
        cartesian = np.asarray(
            (velocity.x_m_s, velocity.y_m_s, velocity.z_m_s),
            dtype=np.float64,
        )
        residual = np.asarray(result.cartesian_constraint_matrix) @ cartesian - np.asarray(
            result.joint_constraint_matrix_m
        ) @ analytical
        errors.append(error)
        residuals.append(float(np.max(np.abs(residual))))

    error_array = np.asarray(errors)
    residual_array = np.asarray(residuals)
    return {
        "acceptance": {
            "max_abs_joint_rate_error_rad_s_lt": 1e-5,
            "p99_abs_joint_rate_error_rad_s_lt": 1e-6,
            "max_constraint_residual_m_s_lt": 1e-10,
        },
        "finite_difference_step_s": FINITE_DIFFERENCE_STEP_S,
        "max_abs_joint_rate_error_rad_s": float(np.max(error_array)),
        "max_cartesian_speed_m_s": MAX_CARTESIAN_SPEED_M_S,
        "max_constraint_residual_m_s": float(np.max(residual_array)),
        "p99_abs_joint_rate_error_rad_s": float(np.percentile(error_array, 99.0)),
        "random_seed": RANDOM_SEED,
        "sample_count": SAMPLE_COUNT,
        "sampling_attempts": attempts,
        "source_geometry": "williams_2016",
        "status": "pass"
        if (
            float(np.max(error_array)) < 1e-5
            and float(np.percentile(error_array, 99.0)) < 1e-6
            and float(np.max(residual_array)) < 1e-10
        )
        else "fail",
    }


def main() -> None:
    """Write the deterministic validation report below artifacts."""

    output_path = Path(__file__).resolve().parents[1] / "artifacts/differential_validation.json"
    report = validation_report()
    output_path.write_text(
        json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    if report["status"] != "pass":
        raise SystemExit("differential kinematics validation failed")


if __name__ == "__main__":
    main()
