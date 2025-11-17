"""
Base service class for PyFTP server components.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from core.exceptions import PyFTPError, ConfigError, ServerError, ValidationError


class BaseService(ABC):
    """Base service class providing common functionality for all services."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)