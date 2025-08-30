"""
FTP server management functionality.
"""

import os
import socket
import warnings
import logging
from threading import Thread, Event

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer


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
            self.server.serve_forever(timeout=0.5, blocking=False)
    
    def stop(self):
        """Stop the FTP server thread."""
        self._stop_event.set()
        self.server.close_all()


class CustomFTPHandler(FTPHandler):
    """Custom FTP handler with logging callbacks."""
    
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


class FTPServerManager:
    """Manager for the FTP server lifecycle."""
    
    def __init__(self):
        self.ftp_server_thread = None
        self.server_instance = None
    
    def is_port_available(self, port):
        """Check if a port is available."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", port))
            s.close()
            return True
        except:
            return False
    
    def is_port_range_available(self, start, end):
        """Check if a port range is available."""
        for port in range(start, end + 1):
            if not self.is_port_available(port):
                return False
        return True
    
    def is_running(self):
        """Check if the server is currently running."""
        return self.ftp_server_thread and self.ftp_server_thread.is_alive()
    
    def start_server(self, config):
        """Start the FTP server with the given configuration."""
        try:
            authorizer = DummyAuthorizer()
            authorizer.add_anonymous(config['directory'], perm="elradfmw")
            
            # Configure the custom handler
            handler = CustomFTPHandler
            handler.authorizer = authorizer
            handler.encoding = config['encoding']
            handler.log_prefix = "%(remote_ip)s:%(remote_port)s"
            
            # Set passive ports if enabled
            if config['passive']:
                handler.passive_ports = range(
                    config['passive_start'], 
                    config['passive_end'] + 1
                )
            
            # Choose server class based on threading setting
            server_class = ThreadedFTPServer if config['threading'] else FTPServer
            self.server_instance = server_class(("0.0.0.0", config['port']), handler)
            self.server_instance.max_cons = 256
            self.server_instance.max_cons_per_ip = 5
            
            # Start the server in a thread
            self.ftp_server_thread = FTPServerThread(self.server_instance)
            self.ftp_server_thread.start()
            
            if config['passive']:
                logging.info(f"被动模式已启用 - 端口范围: {config['passive_start']}-{config['passive_end']}")
            
            return True
        except Exception as e:
            logging.error(f"启动服务器失败: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the FTP server."""
        if self.is_running():
            try:
                self.ftp_server_thread.stop()
                self.ftp_server_thread.join(timeout=2.0)
                
                if self.ftp_server_thread.is_alive():
                    logging.warning("服务器线程仍在运行，强制终止")
                    self.server_instance.close_all()
                
                self.ftp_server_thread = None
                self.server_instance = None
                return True
            except Exception as e:
                logging.error(f"停止服务器失败: {str(e)}")
                return False
        return True