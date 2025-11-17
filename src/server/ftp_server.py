"""
FTP server management functionality.
"""

import os
import socket
import warnings
import logging
from threading import Thread, Event
from typing import Dict, Any, Optional, Type, Tuple, Union
from datetime import datetime

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer

from core.base_service import BaseService
from core.interfaces import ServerManager
from core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END
)
from core.exceptions import ServerError, ValidationError
from core.error_handler import handle_errors, get_error_details
from server.validators import (
    validate_port, validate_port_range, validate_passive_port_range,
    validate_server_directory, is_port_available, is_port_range_available
)
from server.connection_counter import get_connection_counter


# 抑制不必要的警告
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="write permissions assigned to anonymous user")


class FTPServerThread(Thread, BaseService):
    """Thread for running the FTP server."""
    
    def __init__(self, server):
        Thread.__init__(self)
        BaseService.__init__(self)
        self.server = server
        self._stop_event = Event()
        self.daemon = True
    
    def run(self):
        """Run the FTP server in a loop until stopped."""
        while not self._stop_event.is_set():
            self.server.serve_forever(timeout=0.1, blocking=False)  # 减少超时时间以提高响应性
    
    def stop(self):
        """Stop the FTP server thread."""
        self._stop_event.set()
        self.server.close_all()


class CustomFTPHandler(FTPHandler):
    """Custom FTP handler with logging callbacks."""
    
    # 明确定义passive_ports类型
    passive_ports: Optional[range] = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Passive ports will be set from config in the manager
        # 获取连接计数器实例
        self.connection_counter = get_connection_counter()
        # 初始化日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def on_connect(self):
        """Callback when a client connects."""
        self.logger.info(f"新连接来自: {self.remote_ip}:{self.remote_port}")
        # 增加连接计数
        self.connection_counter.increment()
    
    def on_login(self, username):
        """Callback when a user logs in."""
        self.logger.info(f"用户登录: {username}@{self.remote_ip}")
    
    def on_disconnect(self):
        """Callback when a client disconnects."""
        self.logger.info(f"连接关闭: {self.remote_ip}:{self.remote_port}")
        # 减少连接计数
        self.connection_counter.decrement()

    def on_file_sent(self, file):
        """Callback when a file is sent."""
        # 获取文件大小信息
        try:
            bytes_sent = os.path.getsize(file)
            self.logger.info(f"文件发送完成: {file} ({bytes_sent} bytes)")
        except Exception as e:
            self.logger.warning(f"文件发送完成但无法获取大小: {file} (错误: {str(e)})")

    def on_file_received(self, file):
        """Callback when a file is received."""
        self.logger.info(f"文件接收完成: {file}")

    def on_incomplete_file_sent(self, file):
        """Callback when an incomplete file is sent."""
        self.logger.warning(f"不完整文件发送: {file}")

    def on_incomplete_file_received(self, file):
        """Callback when an incomplete file is received."""
        self.logger.warning(f"不完整文件接收: {file}")

    def on_error(self, e):
        """Callback when an error occurs."""
        self.logger.error(f"FTP处理错误: {str(e)}")


class FTPServerManager(BaseService, ServerManager):
    """Manager for the FTP server lifecycle."""
    
    def __init__(self):
        BaseService.__init__(self)
        self.ftp_server_thread = None
        self.server_instance = None
        self.connection_counter = get_connection_counter()
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available.
        
        Args:
            port: Port number to check
            
        Returns:
            True if port is available, False otherwise
        """
        try:
            validate_port(port)
        except ValidationError:
            return False
        return is_port_available(port)
    
    def is_port_range_available(self, start: int, end: int) -> bool:
        """Check if a port range is available.
        
        Args:
            start: Start port number (inclusive)
            end: End port number (inclusive)
            
        Returns:
            True if all ports in range are available, False otherwise
        """
        try:
            validate_port_range(start, end)
        except ValidationError:
            return False
        return is_port_range_available(start, end)
    
    def is_running(self) -> bool:
        """Check if the server is currently running.
        
        Returns:
            True if server is running, False otherwise
        """
        if self.ftp_server_thread is None:
            return False
        return self.ftp_server_thread.is_alive()
    
    def get_connection_count(self) -> int:
        """Get the number of active connections.
        
        Returns:
            Number of active connections
        """
        return self.connection_counter.get_count()
    
    @handle_errors(default_return=False, log_errors=True)
    def start_server(self, config: Dict[str, Any]) -> bool:
        """Start the FTP server with the given configuration.
        
        Args:
            config: Server configuration dictionary
            
        Returns:
            True if server started successfully, False otherwise
            
        Raises:
            ServerError: If there's an error starting the server
            ValidationError: If configuration validation fails
        """
        try:
            # Validate configuration
            self._validate_config(config)
            
            # Reset connection count
            self.connection_counter.reset()
            
            authorizer = DummyAuthorizer()
            directory = config.get('directory', DEFAULT_DIRECTORY)
            authorizer.add_anonymous(directory, perm="elradfmw")
            
            # Configure the custom handler
            handler = CustomFTPHandler
            handler.authorizer = authorizer
            handler.encoding = config.get('encoding', 'utf-8')
            handler.log_prefix = "%(remote_ip)s:%(remote_port)s"
            
            # 设置缓冲区大小以提高性能
            handler.dtp_handler.timeout = 30
            handler.timeout = 600
            handler.banner = "PyFTP Server ready"
            
            # Choose server class based on threading setting
            use_threading = config.get('threading', True)
            server_class = ThreadedFTPServer if use_threading else FTPServer
            port = config.get('port', DEFAULT_PORT)
            self.server_instance = server_class(("0.0.0.0", port), handler)
            
            # Set passive ports if enabled
            if config.get('passive', DEFAULT_PASSIVE_MODE) and self.server_instance:
                passive_start = config.get('passive_start', DEFAULT_PASSIVE_START)
                passive_end = config.get('passive_end', DEFAULT_PASSIVE_END)
                handler.passive_ports = range(passive_start, passive_end + 1)
            
            # 优化服务器配置以提高性能
            self.server_instance.max_cons = 1024  # 增加最大连接数
            self.server_instance.max_cons_per_ip = 20  # 增加每IP最大连接数
            
            # 添加更多性能优化配置
            self.server_instance.handler.timeout = 600  # 连接超时时间
            self.server_instance.handler.dtp_handler.timeout = 30  # 数据传输超时时间
            self.server_instance.handler.banner = "PyFTP Server ready"  # 服务器横幅
            
            # 进一步优化性能
            handler.tcp_no_delay = True  # 启用TCP_NODELAY
            handler.permit_foreign_addresses = True  # 允许外部地址
            handler.masquerade_address = None  # 不伪装地址
            
            # 优化缓冲区大小
            handler.ac_in_buffer_size = 65536
            handler.ac_out_buffer_size = 65536
            
            # Start the server in a thread
            self.ftp_server_thread = FTPServerThread(self.server_instance)
            self.ftp_server_thread.start()
            
            if config.get('passive', DEFAULT_PASSIVE_MODE):
                passive_start = config.get('passive_start', DEFAULT_PASSIVE_START)
                passive_end = config.get('passive_end', DEFAULT_PASSIVE_END)
                self.log_info(f"被动模式已启用 - 端口范围: {passive_start}-{passive_end}")
            
            self.log_info(f"FTP服务器启动成功 - 端口: {port}, 目录: {directory}")
            return True
        except Exception as e:
            error_details = get_error_details(e)
            self.log_error(f"启动服务器失败: {str(e)} - 详细信息: {error_details}")
            raise ServerError(f"启动服务器失败: {str(e)}", error_code="SRV002", details=error_details)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate server configuration.
        
        Args:
            config: Server configuration dictionary
            
        Raises:
            ValidationError: If configuration validation fails
        """
        if not config:
            raise ValidationError("服务器配置不能为空")
            
        # Validate port
        port = config.get('port', DEFAULT_PORT)
        validate_port(port)
        
        # Validate directory
        directory = config.get('directory', DEFAULT_DIRECTORY)
        validate_server_directory(directory)
        
        # Validate passive mode settings
        if config.get('passive', DEFAULT_PASSIVE_MODE):
            passive_start = config.get('passive_start', DEFAULT_PASSIVE_START)
            passive_end = config.get('passive_end', DEFAULT_PASSIVE_END)
            validate_passive_port_range(passive_start, passive_end)
    
    @handle_errors(default_return=True, log_errors=True)
    def stop_server(self) -> bool:
        """Stop the FTP server.
        
        Returns:
            True if server stopped successfully or was not running, False on error
        """
        if self.is_running() and self.ftp_server_thread is not None:
            try:
                self.ftp_server_thread.stop()
                self.ftp_server_thread.join(timeout=2.0)
                
                if self.ftp_server_thread.is_alive():
                    self.log_warning("服务器线程仍在运行，强制终止")
                    if self.server_instance:
                        self.server_instance.close_all()
                
                self.ftp_server_thread = None
                self.server_instance = None
                self.connection_counter.reset()
                self.log_info("FTP服务器已停止")
                return True
            except Exception as e:
                error_details = get_error_details(e)
                self.log_error(f"停止服务器失败: {str(e)} - 详细信息: {error_details}")
                return False
        return True