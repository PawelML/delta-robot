"""Domain errors shared by forward and inverse kinematics."""


class KinematicsError(ValueError):
    """Base class for expected position-kinematics failures."""


class AssemblyConstraintError(KinematicsError):
    """Raised when an input or result violates the selected assembly branch."""


class JointLimitError(KinematicsError):
    """Raised when an angle lies outside an inclusive actuator limit."""


class UnsupportedAssemblyModeError(KinematicsError):
    """Raised when kinematics does not implement the requested branch."""
