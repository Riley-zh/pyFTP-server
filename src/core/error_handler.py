"""
Error handling utilities for PyFTP server.
"""

import logging
import traceback
from typing import Callable, Any, Optional
from functools import wraps

from core.exceptions import PyFTPError


def handle_errors(default_return=None, log_errors=True):
    """
    Decorator for handling errors in functions.
    
    Args:
        default_return: Value to return when an error occurs
        log_errors: Whether to log errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except PyFTPError as e:
                if log_errors:
                    logging.error(f"PyFTP error in {func.__name__}: {str(e)}")
                    logging.debug(f"Traceback: {traceback.format_exc()}")
                return default_return
            except Exception as e:
                if log_errors:
                    logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    logging.debug(f"Traceback: {traceback.format_exc()}")
                return default_return
        return wrapper
    return decorator


def safe_call(func: Callable, *args, default_return=None, **kwargs) -> Any:
    """
    Safely call a function with error handling.
    
    Args:
        func: Function to call
        *args: Positional arguments
        default_return: Value to return when an error occurs
        **kwargs: Keyword arguments
        
    Returns:
        Function result or default_return if an error occurs
    """
    try:
        return func(*args, **kwargs)
    except PyFTPError as e:
        logging.error(f"PyFTP error in {func.__name__}: {str(e)}")
        logging.debug(f"Traceback: {traceback.format_exc()}")
        return default_return
    except Exception as e:
        logging.error(f"Unexpected error in {func.__name__}: {str(e)}")
        logging.debug(f"Traceback: {traceback.format_exc()}")
        return default_return


def format_error(error: Exception) -> str:
    """
    Format an error for display.
    
    Args:
        error: Exception to format
        
    Returns:
        Formatted error string
    """
    if isinstance(error, PyFTPError):
        return str(error)
    else:
        return f"Unexpected error: {str(error)}"


def get_error_details(error: Exception) -> dict:
    """
    Get detailed information about an error.
    
    Args:
        error: Exception to analyze
        
    Returns:
        Dictionary with error details
    """
    details = {
        'type': type(error).__name__,
        'message': str(error),
        'traceback': traceback.format_exc()
    }
    
    if isinstance(error, PyFTPError):
        details['error_code'] = getattr(error, 'error_code', None)
        details['details'] = getattr(error, 'details', {})
    
    return details