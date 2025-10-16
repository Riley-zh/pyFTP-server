"""
Custom exceptions for PyFTP server.
"""

class PyFTPError(Exception):
    """Base exception for PyFTP application."""
    pass

class ConfigError(PyFTPError):
    """Exception raised for configuration errors."""
    pass

class ServerError(PyFTPError):
    """Exception raised for server errors."""
    pass

class ValidationError(PyFTPError):
    """Exception raised for validation errors."""
    pass