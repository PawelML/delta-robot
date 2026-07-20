import math

from hypothesis import given
from hypothesis import strategies as st

from delta_model import AssemblyMode, CartesianPosition, JointAngles

FINITE_FLOATS = st.floats(allow_nan=False, allow_infinity=False, width=64)


@given(x=FINITE_FLOATS, y=FINITE_FLOATS, z=FINITE_FLOATS)
def test_cartesian_position_preserves_si_components(x: float, y: float, z: float) -> None:
    position = CartesianPosition(x_m=x, y_m=y, z_m=z)

    assert position == CartesianPosition(x_m=x, y_m=y, z_m=z)


@given(theta_1=FINITE_FLOATS, theta_2=FINITE_FLOATS, theta_3=FINITE_FLOATS)
def test_joint_angles_preserve_radian_components(
    theta_1: float,
    theta_2: float,
    theta_3: float,
) -> None:
    angles = JointAngles(
        theta_1_rad=theta_1,
        theta_2_rad=theta_2,
        theta_3_rad=theta_3,
    )

    assert math.isfinite(angles.theta_1_rad)
    assert math.isfinite(angles.theta_2_rad)
    assert math.isfinite(angles.theta_3_rad)


def test_first_supported_assembly_mode_is_explicit() -> None:
    assert AssemblyMode.KNEE_OUT_PLATFORM_BELOW.value == "knee_out_platform_below"
