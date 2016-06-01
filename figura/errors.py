"""
Definition of the config-related exception types.
"""

################################################################################
# Exception types

class ConfigError(Exception):
    """
    Base class for config-related exceptions
    """
    pass

class ConfigParsingError(ConfigError):
    """
    Exception raised when configuration parsing fails
    """
    pass

class ConfigValueError(ConfigError):
    """
    Exception raised when configuration contains bad values or is missing values
    """
    pass

################################################################################
