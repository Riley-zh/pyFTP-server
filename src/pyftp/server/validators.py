"""
Validation utilities for FTP server configuration.
"""

import socket
from typing import Tuple

from pyftp.core.constants import MIN_PORT, MAX_PORT, MIN_PASSIVE_PORT, MAX_PASSIVE_PORT
from pyftp.core.exceptions import ValidationError
from pyftp.utils.helpers import validate_directory
from pyftp.server.port_cache import get_port_cache


def validate_port(port: int) -> None:
    """Validate port number.
    
    Args:
        port: Port number to validate
        
    Raises:
        ValidationError: If port is invalid
    """
    if not isinstance(port, int) or not (MIN_PORT <= port <= MAX_PORT):
        raise ValidationError(f"端口必须是 {MIN_PORT}-{MAX_PORT} 范围内的整数")


def validate_port_range(start: int, end: int) -> None:
    """Validate port range.
    
    Args:
        start: Start port number
        end: End port number
        
    Raises:
        ValidationError: If port range is invalid
    """
    validate_port(start)
    validate_port(end)
    
    if start >= end:
        raise ValidationError("端口范围无效: 起始端口必须小于结束端口")


def validate_passive_port_range(start: int, end: int) -> None:
    """Validate passive port range.
    
    Args:
        start: Start port number
        end: End port number
        
    Raises:
        ValidationError: If passive port range is invalid
    """
    if not isinstance(start, int) or not (MIN_PASSIVE_PORT <= start <= MAX_PASSIVE_PORT):
        raise ValidationError(f"被动起始端口必须是 {MIN_PASSIVE_PORT}-{MAX_PASSIVE_PORT} 范围内的整数")
        
    if not isinstance(end, int) or not (MIN_PASSIVE_PORT <= end <= MAX_PASSIVE_PORT):
        raise ValidationError(f"被动结束端口必须是 {MIN_PASSIVE_PORT}-{MAX_PASSIVE_PORT} 范围内的整数")
        
    if start >= end:
        raise ValidationError("被动端口范围无效: 起始端口必须小于结束端口")


def validate_server_directory(directory: str) -> None:
    """Validate server directory.
    
    Args:
        directory: Directory path to validate
        
    Raises:
        ValidationError: If directory is invalid
    """
    if not validate_directory(directory):
        raise ValidationError(f"目录不存在或无法访问: {directory}")


def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if a port is available on the given host.
    
    Args:
        port: Port number to check
        host: Host address to bind to, defaults to "0.0.0.0"
        
    Returns:
        True if port is available, False otherwise
    """
    # Use port cache for better performance
    port_cache = get_port_cache()
    return port_cache.is_port_available(port, host)


def is_port_range_available(start: int, end: int, host: str = "0.0.0.0") -> bool:
    """Check if a range of ports is available on the given host.
    
    Args:
        start: Start port number (inclusive)
        end: End port number (inclusive)
        host: Host address to bind to, defaults to "0.0.0.0"
        
    Returns:
        True if all ports in range are available, False otherwise
    """
    # Use port cache for better performance
    port_cache = get_port_cache()
    return port_cache.is_port_range_available(start, end, host)