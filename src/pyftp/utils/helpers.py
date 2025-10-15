"""
Helper functions for PyFTP server.
"""

import os
import socket
from typing import Optional


def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a port is available on the given host.
    
    Args:
        port: Port number to check
        host: Host address to bind to, defaults to "0.0.0.0"
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False


def is_port_range_available(start: int, end: int, host: str = "0.0.0.0") -> bool:
    """Check if a range of ports is available on the given host.
    
    Args:
        start: Start port number (inclusive)
        end: End port number (inclusive)
        host: Host address to bind to, defaults to "0.0.0.0"
        
    Returns:
        True if all ports in range are available, False otherwise
    """
    for port in range(start, end + 1):
        if not is_port_available(port, host):
            return False
    return True


def validate_directory(path: str) -> bool:
    """Validate if a directory path exists and is accessible.
    
    Args:
        path: Directory path to validate
        
    Returns:
        True if directory is valid, False otherwise
    """
    return os.path.isdir(path)


def get_app_data_dir(app_name: str) -> str:
    """Get application data directory based on OS.
    
    Args:
        app_name: Name of the application
        
    Returns:
        Path to application data directory
    """
    # This is a simplified version - in production, you might want to use
    # platform-specific directories
    return os.path.expanduser(f"~/.{app_name}")


def sanitize_path(path: str) -> str:
    """Sanitize a file path by resolving and normalizing it.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path
    """
    return os.path.normpath(os.path.abspath(path))