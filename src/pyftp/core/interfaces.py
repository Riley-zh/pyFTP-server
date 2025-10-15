"""
Interfaces for PyFTP server components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from pathlib import Path


class ServerManager(ABC):
    """Abstract interface for server management."""
    
    @abstractmethod
    def start_server(self, config: Dict[str, Any]) -> bool:
        """Start the server with given configuration."""
        pass
    
    @abstractmethod
    def stop_server(self) -> bool:
        """Stop the server."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if server is running."""
        pass
    
    @abstractmethod
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        pass
    
    @abstractmethod
    def is_port_range_available(self, start: int, end: int) -> bool:
        """Check if a port range is available."""
        pass
    
    @abstractmethod
    def get_connection_count(self) -> int:
        """Get current connection count."""
        pass


class ConfigManager(ABC):
    """Abstract interface for configuration management."""
    
    @abstractmethod
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from storage."""
        pass
    
    @abstractmethod
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to storage."""
        pass
    
    def get_config_path(self) -> Path:
        """Get the configuration file path.
        
        Returns:
            Path to the configuration file
        """
        raise NotImplementedError("Subclasses should implement this method")
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values.
        
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses should implement this method")