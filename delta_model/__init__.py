"""Authoritative Python model for the rotary delta robot."""

from delta_model.conventions import AssemblyMode, CartesianPoint, CartesianPosition, JointAngles
from delta_model.errors import (
    AssemblyConstraintError,
    JointLimitError,
    KinematicsError,
    UnsupportedAssemblyModeError,
)
from delta_model.forward_kinematics import (
    AmbiguousForwardSolutionError,
    ArmForwardPose,
    DegenerateSphereGeometryError,
    ForwardKinematicsError,
    ForwardKinematicsResult,
    InvalidAnglesError,
    UnreachableAnglesError,
    forward_kinematics,
    intersect_three_equal_spheres,
)
from delta_model.geometry import DeltaGeometry, GeometryValidationError
from delta_model.inverse_kinematics import (
    AmbiguousAssemblyError,
    ArmInverseSolution,
    DegeneratePositionError,
    InvalidPositionError,
    InverseKinematicsError,
    InverseKinematicsResult,
    UnreachablePositionError,
    inverse_kinematics,
    solve_arm_inverse,
)

__all__ = [
    "AmbiguousAssemblyError",
    "AmbiguousForwardSolutionError",
    "ArmForwardPose",
    "ArmInverseSolution",
    "AssemblyConstraintError",
    "AssemblyMode",
    "CartesianPoint",
    "CartesianPosition",
    "DegeneratePositionError",
    "DegenerateSphereGeometryError",
    "DeltaGeometry",
    "ForwardKinematicsError",
    "ForwardKinematicsResult",
    "GeometryValidationError",
    "InvalidAnglesError",
    "InvalidPositionError",
    "InverseKinematicsError",
    "InverseKinematicsResult",
    "JointAngles",
    "JointLimitError",
    "KinematicsError",
    "UnreachableAnglesError",
    "UnreachablePositionError",
    "UnsupportedAssemblyModeError",
    "forward_kinematics",
    "intersect_three_equal_spheres",
    "inverse_kinematics",
    "solve_arm_inverse",
]
__version__ = "0.1.0"
