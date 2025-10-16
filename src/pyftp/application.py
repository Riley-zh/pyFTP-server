"""
Main application class for PyFTP server.
Orchestrates the interaction between different components.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from pyftp.core.interfaces import ServerManager, ConfigManager
from pyftp.server.ftp_server import FTPServerManager
from pyftp.config.manager import ConfigManager as ConfigManagerImpl
from pyftp.core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END, 
    DEFAULT_ENCODING_IDX, DEFAULT_THREADING_IDX
)
from pyftp.core.exceptions import PyFTPError, ConfigError, ServerError


class PyFTPApplication:
    """Main application class that coordinates all components."""
    
    def __init__(self, config_file: str = "ftpserver.ini"):
        """Initialize the PyFTP application.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config_manager: ConfigManager = ConfigManagerImpl(config_file)
        self.server_manager: ServerManager = FTPServerManager()
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize the application.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self._is_initialized:
            return True
            
        try:
            # Setup logging
            self._setup_logging()
            
            # Load configuration
            self._load_configuration()
            
            self._is_initialized = True
            logging.info("PyFTP应用程序初始化成功")
            return True
        except Exception as e:
            logging.error(f"应用程序初始化失败: {str(e)}")
            return False
    
    def _setup_logging(self) -> None:
        """Setup application logging."""
        # Logging is typically setup in the GUI, but we ensure it's configured
        root_logger = logging.getLogger()
        if not root_logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    def _load_configuration(self) -> None:
        """Load application configuration."""
        try:
            config_data = self.config_manager.load_config()
            if not config_data:
                logging.info("未找到配置文件，使用默认配置")
        except ConfigError as e:
            logging.error(f"配置加载失败: {str(e)}")
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get current configuration.
        
        Returns:
            Current configuration dictionary or None if not loaded
        """
        try:
            return self.config_manager.load_config()
        except ConfigError as e:
            logging.error(f"配置获取失败: {str(e)}")
            return None
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration.
        
        Args:
            config_data: Configuration data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.config_manager.save_config(config_data)
        except (ConfigError, PyFTPError) as e:
            logging.error(f"配置保存失败: {str(e)}")
            return False
    
    def start_server(self, config: Dict[str, Any]) -> bool:
        """Start the FTP server.
        
        Args:
            config: Server configuration
            
        Returns:
            True if server started successfully, False otherwise
        """
        try:
            return self.server_manager.start_server(config)
        except (ServerError, PyFTPError) as e:
            logging.error(f"服务器启动失败: {str(e)}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the FTP server.
        
        Returns:
            True if server stopped successfully or was not running, False on error
        """
        try:
            return self.server_manager.stop_server()
        except PyFTPError as e:
            logging.error(f"服务器停止失败: {str(e)}")
            return False
    
    def is_server_running(self) -> bool:
        """Check if the FTP server is running.
        
        Returns:
            True if server is running, False otherwise
        """
        return self.server_manager.is_running()
    
    def get_connection_count(self) -> int:
        """Get the number of active connections.
        
        Returns:
            Number of active connections
        """
        return self.server_manager.get_connection_count()
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        return self.server_manager.is_port_available(port)
    
    def is_port_range_available(self, start: int, end: int) -> bool:
        """Check if a port range is available.
        
        Args:
            start: Start port (inclusive)
            end: End port (inclusive)
            
        Returns:
            True if all ports in range are available, False otherwise
        """
        return self.server_manager.is_port_range_available(start, end)
    
    def get_config_file_path(self) -> Path:
        """Get the configuration file path.
        
        Returns:
            Path to the configuration file
        """
        # Use the actual method if available, otherwise fallback
        return Path(self.config_file)
    
    def reset_config_to_defaults(self) -> bool:
        """Reset configuration to default values.
        
        Returns:
            True if successful, False otherwise
        """
        default_config = {
            'port': DEFAULT_PORT,
            'directory': DEFAULT_DIRECTORY,
            'passive': DEFAULT_PASSIVE_MODE,
            'passive_start': DEFAULT_PASSIVE_START,
            'passive_end': DEFAULT_PASSIVE_END,
            'encoding_idx': DEFAULT_ENCODING_IDX,
            'threading_idx': DEFAULT_THREADING_IDX
        }
        return self.save_config(default_config)