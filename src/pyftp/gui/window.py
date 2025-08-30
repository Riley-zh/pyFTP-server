"""
Main window for the PyFTP server application.
"""

import sys
import os
import logging
import configparser
import warnings
import socket
from threading import Thread, Event
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QTimer

from pyftp.gui.components.config_panel import ConfigPanel
from pyftp.gui.components.control_panel import ControlPanel
from pyftp.gui.components.log_panel import LogPanel
from pyftp.gui.components.user_panel import UserPanel
from pyftp.server.ftp_server import FTPServerManager
from pyftp.config.manager import ConfigManager


# 抑制不必要的警告
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="write permissions assigned to anonymous user")


class FTPWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config_file = "ftpserver.ini"
        self.config_manager = ConfigManager(self.config_file)
        self.ftp_server_manager = FTPServerManager()
        
        self.setup_ui()
        self.setup_logging()
        self.load_config()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("PyFTP Server")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 配置面板
        self.config_panel = ConfigPanel()
        main_layout.addWidget(self.config_panel)
        
        # 用户信息面板
        self.user_panel = UserPanel()
        main_layout.addWidget(self.user_panel)
        
        # 控制按钮面板
        self.control_panel = ControlPanel()
        self.control_panel.start_btn.clicked.connect(self.toggle_server)
        self.control_panel.save_btn.clicked.connect(self.save_config)
        self.control_panel.reload_btn.clicked.connect(self.reload_config)
        self.control_panel.clear_log_btn.clicked.connect(self.clear_log)
        main_layout.addWidget(self.control_panel)
        
        # 日志显示面板
        self.log_panel = LogPanel()
        self.log_panel.log_level_combo.currentIndexChanged.connect(self.filter_logs)
        main_layout.addWidget(self.log_panel)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("服务器已停止")
        
        # 初始化被动模式字段状态
        self.config_panel.toggle_passive_fields()
    
    def setup_logging(self):
        """Setup logging for the application."""
        from pyftp.server.logger import QtLogHandler
        
        self.log_handler = QtLogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(self.log_handler)
        
        # 设置pyftpdlib的日志级别
        ftp_logger = logging.getLogger('pyftpdlib')
        ftp_logger.setLevel(logging.INFO)
        ftp_logger.addHandler(self.log_handler)
    
    def append_log(self, message, level):
        """Append log message to the log panel."""
        self.log_panel.append_log(message, level)
    
    def filter_logs(self):
        """Filter logs based on selected level."""
        self.log_panel.filter_logs()
    
    def clear_log(self):
        """Clear log display."""
        self.log_panel.clear_log()
        logging.info("日志已清空")
    
    def browse_dir(self):
        """Open directory browser."""
        directory = QFileDialog.getExistingDirectory(self, "选择FTP根目录")
        if directory:
            self.config_panel.dir_edit.setText(directory)
    
    def load_config(self):
        """Load configuration from file."""
        config_data = self.config_manager.load_config()
        if config_data:
            self.config_panel.load_config(config_data)
            logging.info("配置文件已加载")
        else:
            logging.warning("配置文件不存在，使用默认配置")
            # 创建默认配置
            self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        config_data = self.config_panel.get_config()
        success = self.config_manager.save_config(config_data)
        if success:
            logging.info("配置保存成功")
        else:
            logging.error("保存配置失败")
    
    def reload_config(self):
        """Reload configuration and restart server if running."""
        if self.ftp_server_manager.is_running():
            logging.info("正在重新加载配置...")
            self.stop_server()
            self.start_server()
    
    def start_server(self):
        """Start the FTP server."""
        config = self.config_panel.get_config()
        
        if not self.ftp_server_manager.is_port_available(config['port']):
            logging.error(f"端口 {config['port']} 已被占用，请选择其他端口")
            QMessageBox.critical(self, "端口冲突", f"端口 {config['port']} 已被占用，请选择其他端口")
            return False
        
        if config['passive']:
            if config['passive_start'] >= config['passive_end']:
                logging.error("被动端口范围无效: 起始端口必须小于结束端口")
                QMessageBox.critical(self, "配置错误", "被动端口范围无效: 起始端口必须小于结束端口")
                return False
            
            if not self.ftp_server_manager.is_port_range_available(config['passive_start'], config['passive_end']):
                logging.error("被动端口范围已被占用或不可用")
                QMessageBox.critical(self, "端口冲突", "被动端口范围已被占用或不可用")
                return False
        
        if not os.path.isdir(config['directory']):
            logging.error(f"目录不存在: {config['directory']}")
            QMessageBox.critical(self, "目录错误", f"目录不存在: {config['directory']}")
            return False
        
        try:
            success = self.ftp_server_manager.start_server(config)
            if success:
                self.control_panel.start_btn.setText("停止服务器")
                self.status_bar.showMessage(
                    f"服务器运行中: 端口 {config['port']}, "
                    f"目录 {config['directory']}, "
                    f"编码 {config['encoding'].upper()}, "
                    f"{'多线程' if config['threading'] else '单线程'}模式"
                )
                self.control_panel.reload_btn.setEnabled(True)
                logging.info(f"FTP服务器已启动 ({'多线程' if config['threading'] else '单线程'}模式)")
                return True
            else:
                logging.error("启动服务器失败")
                QMessageBox.critical(self, "服务器错误", "启动服务器失败")
                return False
        except Exception as e:
            logging.error(f"启动服务器失败: {str(e)}")
            QMessageBox.critical(self, "服务器错误", f"启动服务器失败: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the FTP server."""
        if self.ftp_server_manager.is_running():
            try:
                self.ftp_server_manager.stop_server()
                self.control_panel.start_btn.setText("启动服务器")
                self.status_bar.showMessage("服务器已停止")
                self.control_panel.reload_btn.setEnabled(False)
                logging.info("FTP服务器已停止")
            except Exception as e:
                logging.error(f"停止服务器失败: {str(e)}")
                QMessageBox.critical(self, "服务器错误", f"停止服务器失败: {str(e)}")
    
    def toggle_server(self):
        """Toggle server start/stop."""
        if self.ftp_server_manager.is_running():
            self.stop_server()
        else:
            self.start_server()
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.ftp_server_manager.is_running():
            self.stop_server()
            QTimer.singleShot(500, self.close)
            event.ignore()
        else:
            event.accept()