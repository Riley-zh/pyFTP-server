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

from pyftp.core.interfaces import ServerManager
from pyftp.core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END
)
from pyftp.utils.helpers import is_port_available, is_port_range_available


# 抑制不必要的警告
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="write permissions assigned to anonymous user")


class FTPServerThread(Thread):
    """Thread for running the FTP server."""
    
    def __init__(self, server):
        super().__init__()
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
    
    def on_connect(self):
        """Callback when a client connects."""
        logging.info(f"新连接来自: {self.remote_ip}:{self.remote_port}")
    
    def on_login(self, username):
        """Callback when a user logs in."""
        logging.info(f"用户登录: {username}@{self.remote_ip}")
    
    def on_disconnect(self):
        """Callback when a client disconnects."""
        logging.info(f"连接关闭: {self.remote_ip}:{self.remote_port}")

    def on_file_sent(self, file):
        """Callback when a file is sent."""
        # 获取文件大小信息
        try:
            bytes_sent = os.path.getsize(file)
            logging.info(f"文件发送完成: {file} ({bytes_sent} bytes)")
        except Exception as e:
            logging.warning(f"文件发送完成但无法获取大小: {file} (错误: {str(e)})")

    def on_file_received(self, file):
        """Callback when a file is received."""
        logging.info(f"文件接收完成: {file}")

    def on_incomplete_file_sent(self, file):
        """Callback when an incomplete file is sent."""
        logging.warning(f"不完整文件发送: {file}")

    def on_incomplete_file_received(self, file):
        """Callback when an incomplete file is received."""
        logging.warning(f"不完整文件接收: {file}")

    def on_error(self, e):
        """Callback when an error occurs."""
        logging.error(f"FTP处理错误: {str(e)}")


class FTPServerManager(ServerManager):
    """Manager for the FTP server lifecycle."""
    
    def __init__(self):
        self.ftp_server_thread = None
        self.server_instance = None
        self.active_connections = 0  # 跟踪活动连接数
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        return is_port_available(port)
    
    def is_port_range_available(self, start: int, end: int) -> bool:
        """Check if a port range is available."""
        return is_port_range_available(start, end)
    
    def is_running(self) -> bool:
        """Check if the server is currently running."""
        if self.ftp_server_thread is None:
            return False
        return self.ftp_server_thread.is_alive()
    
    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return self.active_connections
    
    def start_server(self, config: Dict[str, Any]) -> bool:
        """Start the FTP server with the given configuration."""
        try:
            # Reset connection count
            self.active_connections = 0
            
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
                self.server_instance.handler.passive_ports = range(passive_start, passive_end + 1)
            
            # 优化服务器配置以提高性能
            self.server_instance.max_cons = 512  # 增加最大连接数
            self.server_instance.max_cons_per_ip = 10  # 增加每IP最大连接数
            
            # Start the server in a thread
            self.ftp_server_thread = FTPServerThread(self.server_instance)
            self.ftp_server_thread.start()
            
            if config.get('passive', DEFAULT_PASSIVE_MODE):
                passive_start = config.get('passive_start', DEFAULT_PASSIVE_START)
                passive_end = config.get('passive_end', DEFAULT_PASSIVE_END)
                logging.info(f"被动模式已启用 - 端口范围: {passive_start}-{passive_end}")
            
            logging.info(f"FTP服务器启动成功 - 端口: {port}, 目录: {directory}")
            return True
        except Exception as e:
            logging.error(f"启动服务器失败: {str(e)}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the FTP server."""
        if self.is_running() and self.ftp_server_thread is not None:
            try:
                self.ftp_server_thread.stop()
                self.ftp_server_thread.join(timeout=2.0)
                
                if self.ftp_server_thread.is_alive():
                    logging.warning("服务器线程仍在运行，强制终止")
                    if self.server_instance:
                        self.server_instance.close_all()
                
                self.ftp_server_thread = None
                self.server_instance = None
                self.active_connections = 0
                logging.info("FTP服务器已停止")
                return True
            except Exception as e:
                logging.error(f"停止服务器失败: {str(e)}")
                return False
        return True