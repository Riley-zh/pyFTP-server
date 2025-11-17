"""
Interfaces for PyFTP server components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from core.exceptions import ConfigError, ServerError, ValidationError


class ServerManager(ABC):
    """Abstract interface for server management."""
    
    @abstractmethod
    def start_server(self, config: Dict[str, Any]) -> bool:
        """Start the server with given configuration.
        
        Args:
            config: Server configuration dictionary
            
        Returns:
            True if server started successfully, False otherwise
            
        Raises:
            ServerError: If there's an error starting the server
            ValidationError: If configuration validation fails
        """
        pass
    
    @abstractmethod
    def stop_server(self) -> bool:
        """Stop the server.
        
        Returns:
            True if server stopped successfully or was not running, False on error
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if server is running.
        
        Returns:
            True if server is running, False otherwise
        """
        pass
    
    @abstractmethod
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        pass
    
    @abstractmethod
    def is_port_range_available(self, start: int, end: int) -> bool:
        """Check if a port range is available.
        
        Args:
            start: Start port number (inclusive)
            end: End port number (inclusive)
            
        Returns:
            True if all ports in range are available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_connection_count(self) -> int:
        """Get current connection count.
        
        Returns:
            Number of active connections
        """
        pass


class ConfigManager(ABC):
    """Abstract interface for configuration management."""
    
    @abstractmethod
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from storage.
        
        Returns:
            Dict with configuration data or None if file doesn't exist
            
        Raises:
            ConfigError: If there's an error loading the configuration
        """
        pass
    
    @abstractmethod
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to storage.
        
        Args:
            config_data: Dictionary with configuration data
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ConfigError: If there's an error saving the configuration
            ValidationError: If configuration validation fails
        """
        pass
    
    @abstractmethod
    def get_config_path(self) -> Path:
        """Get the configuration file path.
        
        Returns:
            Path to the configuration file
        """
        pass
    
    @abstractmethod
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values.
        
        Returns:
            True if successful, False otherwise
        """
        pass