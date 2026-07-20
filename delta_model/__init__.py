"""Authoritative Python model for the rotary delta robot."""

from delta_model.conventions import AssemblyMode, CartesianPoint, CartesianPosition, JointAngles
from delta_model.geometry import DeltaGeometry, GeometryValidationError
from delta_model.inverse_kinematics import (
    AmbiguousAssemblyError,
    ArmInverseSolution,
    AssemblyConstraintError,
    DegeneratePositionError,
    InvalidPositionError,
    InverseKinematicsError,
    InverseKinematicsResult,
    JointLimitError,
    UnreachablePositionError,
    UnsupportedAssemblyModeError,
    inverse_kinematics,
    solve_arm_inverse,
)

__all__ = [
    "AmbiguousAssemblyError",
    "ArmInverseSolution",
    "AssemblyConstraintError",
    "AssemblyMode",
    "CartesianPoint",
    "CartesianPosition",
    "DegeneratePositionError",
    "DeltaGeometry",
    "GeometryValidationError",
    "InvalidPositionError",
    "InverseKinematicsError",
    "InverseKinematicsResult",
    "JointAngles",
    "JointLimitError",
    "UnreachablePositionError",
    "UnsupportedAssemblyModeError",
    "inverse_kinematics",
    "solve_arm_inverse",
]
__version__ = "0.1.0"
