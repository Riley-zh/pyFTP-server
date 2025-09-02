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
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QTextCursor

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
        
        # 用于异步操作的定时器
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        
        self.setup_ui()
        self.setup_logging()
        self.load_config()
        
        # 启动状态更新定时器
        self.status_update_timer.start(1000)  # 每秒更新一次状态
    
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
        
        # 获取根日志记录器并移除所有现有的处理器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建并添加我们的Qt日志处理器
        self.log_handler = QtLogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        root_logger.addHandler(self.log_handler)
        
        # 设置pyftpdlib的日志级别并添加我们的处理器
        ftp_logger = logging.getLogger('pyftpdlib')
        ftp_logger.setLevel(logging.INFO)
        
        # 移除pyftpdlib的所有现有处理器
        for handler in ftp_logger.handlers[:]:
            ftp_logger.removeHandler(handler)
            
        # 添加我们的处理器
        ftp_logger.addHandler(self.log_handler)
        
        # 记录一条测试日志，确认日志系统工作正常
        logging.info("日志系统初始化完成")
    
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
            # 使用定时器延迟启动以确保服务器完全停止
            QTimer.singleShot(500, self._delayed_start_server)
    
    def _delayed_start_server(self):
        """Wrapper method for starting server with QTimer."""
        self.start_server()
    
    def update_status(self):
        """Update the status bar with server information."""
        if self.ftp_server_manager.is_running():
            config = self.config_panel.get_config()
            conn_count = self.ftp_server_manager.get_connection_count()
            status_text = (f"服务器运行中: 端口 {config['port']}, "
                          f"目录 {config['directory']}, "
                          f"编码 {config['encoding'].upper()}, "
                          f"{'多线程' if config['threading'] else '单线程'}模式, "
                          f"连接数: {conn_count}")
            self.status_bar.showMessage(status_text)
    
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
                self.control_panel.reload_btn.setEnabled(False)
                logging.info("FTP服务器已停止")
                return True
            except Exception as e:
                logging.error(f"停止服务器失败: {str(e)}")
                return False
        return True
    
    def toggle_server(self):
        """Toggle the FTP server on/off."""
        if self.ftp_server_manager.is_running():
            self.stop_server()
        else:
            self.start_server()
    
    def closeEvent(self, a0):
        """Handle window close event."""
        # 停止状态更新定时器
        self.status_update_timer.stop()
        
        # 停止FTP服务器
        if self.ftp_server_manager.is_running():
            reply = QMessageBox.question(
                self, '确认退出', 'FTP服务器正在运行，确定要退出吗？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_server()
                a0.accept()
            else:
                a0.ignore()
                # 重新启动状态更新定时器
                self.status_update_timer.start(1000)
        else:
            a0.accept()