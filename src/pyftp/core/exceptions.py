"""
Custom exceptions for PyFTP server.
"""

class PyFTPError(Exception):
    """Base exception for PyFTP application."""
    
    def __init__(self, message: str, error_code: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

class ConfigError(PyFTPError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, error_code: str = "CFG001", details: dict | None = None):
        super().__init__(message, error_code, details)

class ServerError(PyFTPError):
    """Exception raised for server errors."""
    
    def __init__(self, message: str, error_code: str = "SRV001", details: dict | None = None):
        super().__init__(message, error_code, details)

class ValidationError(PyFTPError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, error_code: str = "VAL001", details: dict | None = None):
        super().__init__(message, error_code, details)