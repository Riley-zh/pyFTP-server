"""
Main window for the PyFTP server application.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
import configparser
import warnings
import socket
from threading import Thread, Event
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QMessageBox, QFileDialog, QGraphicsOpacityEffect
)
from PyQt5.QtCore import QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QEvent

from core.qt_base_service import QtBaseService
from gui.components.config_panel import GuiConfigPanel
from gui.components.control_panel import GuiControlPanel
from gui.components.log_panel import GuiLogPanel
from gui.components.user_panel import GuiUserPanel
from server.ftp_server import FTPServerManager
from config.manager import ConfigManager
from core.constants import STATUS_UPDATE_INTERVAL
from core.interfaces import ServerManager, ConfigManager as ConfigManagerInterface
from core.exceptions import PyFTPError, ConfigError, ServerError, ValidationError
from server.logger import QtLogHandler
from server.connection_counter import get_connection_counter


# 抑制不必要的警告
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="write permissions assigned to anonymous user")


class GuiMainWindow(QMainWindow, QtBaseService):
    """Main application window."""
    
    def __init__(self):
        QMainWindow.__init__(self)
        QtBaseService.__init__(self)
        self.config_file = "ftpserver.ini"
        self.config_manager: ConfigManagerInterface = ConfigManager(self.config_file)
        self.ftp_server_manager: ServerManager = FTPServerManager()
        self.connection_counter = get_connection_counter()
        
        # 用于异步操作的定时器
        self.status_update_timer = QTimer()
        self.status_update_timer.timeout.connect(self.update_status)
        
        self.setup_ui()
        self.setup_logging()
        self.load_config()
        self.connect_signals()
        
        # 启动状态更新定时器
        self.status_update_timer.start(STATUS_UPDATE_INTERVAL)  # 每秒更新一次状态
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("PyFTP Server")
        self.setGeometry(100, 100, 800, 600)
        
        # 移除窗口样式
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 配置面板
        self.config_panel = GuiConfigPanel()
        main_layout.addWidget(self.config_panel)
        
        # 用户信息面板
        self.user_panel = GuiUserPanel()
        main_layout.addWidget(self.user_panel)
        
        # 控制按钮面板
        self.control_panel = GuiControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # 日志显示面板
        self.log_panel = GuiLogPanel()
        main_layout.addWidget(self.log_panel)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("服务器已停止")
        
        # 初始化被动模式字段状态
        self.config_panel.toggle_passive_fields()
    
    def connect_signals(self):
        """Connect UI signals to handlers."""
        # Config panel signals
        self.config_panel.directory_browse_requested.connect(self.browse_dir)
        self.config_panel.config_changed.connect(self.on_config_changed)
        
        # Control panel signals
        self.control_panel.start_btn.clicked.connect(self.toggle_server)
        self.control_panel.save_btn.clicked.connect(self.save_config)
        self.control_panel.reload_btn.clicked.connect(self.reload_config)
        self.control_panel.clear_log_btn.clicked.connect(self.clear_log)
        
        # Log panel signals
        self.log_panel.log_level_combo.currentIndexChanged.connect(self.filter_logs)
    
    def on_config_changed(self):
        """Handle configuration changes."""
        # Could be used to enable/disable save button or show unsaved changes indicator
        pass
    
    def setup_logging(self):
        """Setup logging for the application."""
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
        
        # 设置pyftpdlib的日志级别，但它会继承根日志记录器的处理器
        # 不需要再单独添加处理器，避免重复日志
        ftp_logger = logging.getLogger('pyftpdlib')
        ftp_logger.setLevel(logging.INFO)
        
        # 记录一条测试日志，确认日志系统工作正常
        self.log_info("日志系统初始化完成")
    
    def append_log(self, message, level):
        """Append log message to the log panel."""
        self.log_panel.append_log(message, level)
    
    def filter_logs(self):
        """Filter logs based on selected level."""
        self.log_panel.filter_logs()
    
    def clear_log(self):
        """Clear log display."""
        self.log_panel.clear_log()
        self.log_info("日志已清空")
        self.control_panel.log_cleared.emit()
        
        # 添加视觉反馈动画
        self._animate_widget(self.log_panel, duration=300)
    
    def browse_dir(self):
        """Open directory browser."""
        directory = QFileDialog.getExistingDirectory(self, "选择FTP根目录")
        if directory:
            self.config_panel.dir_edit.setText(str(Path(directory)))
    
    def load_config(self):
        """Load configuration from file."""
        try:
            config_data = self.config_manager.load_config()
            if config_data:
                self.config_panel.load_config(config_data)
                self.log_info("配置文件已加载")
            else:
                self.log_warning("配置文件不存在，使用默认配置")
                # 创建默认配置
                self.save_config()
        except ConfigError as e:
            self.log_error(f"配置加载失败: {str(e)}")
            QMessageBox.critical(self, "配置错误", f"配置加载失败: {str(e)}")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            config_data = self.config_panel.get_config()
            success = self.config_manager.save_config(config_data)
            if success:
                self.log_info("配置保存成功")
                self.control_panel.config_saved.emit()
                
                # 添加视觉反馈动画
                self._animate_widget(self.config_panel, duration=500)
            else:
                self.log_error("保存配置失败")
        except (ConfigError, ValidationError) as e:
            self.log_error(f"配置保存失败: {str(e)}")
            QMessageBox.critical(self, "配置错误", f"配置保存失败: {str(e)}")
    
    def reload_config(self):
        """Reload configuration and restart server if running."""
        if self.ftp_server_manager.is_running():
            self.log_info("正在重新加载配置...")
            self.stop_server()
            # 使用定时器延迟启动以确保服务器完全停止
            QTimer.singleShot(500, self._delayed_start_server)
        else:
            self.control_panel.config_reloaded.emit()
    
    def _delayed_start_server(self):
        """Wrapper method for starting server with QTimer."""
        self.start_server()
    
    def update_status(self):
        """Update the status bar with server information."""
        if self.ftp_server_manager.is_running():
            config = self.config_panel.get_config()
            conn_count = self.connection_counter.get_count()
            status_text = (f"服务器运行中: 端口 {config['port']}, "
                          f"目录 {config['directory']}, "
                          f"编码 {config['encoding']}, "
                          f"{'多线程' if config['threading'] else '单线程'}模式, "
                          f"连接数: {conn_count}")
            self.status_bar.showMessage(status_text)
    
    def validate_config(self):
        """Validate current configuration."""
        errors = self.config_panel.validate_config()
        if errors:
            error_msg = "\n".join(errors)
            self.log_error(f"配置验证失败:\n{error_msg}")
            QMessageBox.critical(self, "配置错误", f"配置验证失败:\n{error_msg}")
            return False
        return True
    
    def start_server(self):
        """Start the FTP server."""
        # Validate configuration first
        if not self.validate_config():
            return False
        
        config = self.config_panel.get_config()
        
        try:
            if not self.ftp_server_manager.is_port_available(config['port']):
                self.log_error(f"端口 {config['port']} 已被占用，请选择其他端口")
                QMessageBox.critical(self, "端口冲突", f"端口 {config['port']} 已被占用，请选择其他端口")
                return False
            
            if config['passive']:
                if not self.ftp_server_manager.is_port_range_available(config['passive_start'], config['passive_end']):
                    self.log_error("被动端口范围已被占用或不可用")
                    QMessageBox.critical(self, "端口冲突", "被动端口范围已被占用或不可用")
                    return False
            
            success = self.ftp_server_manager.start_server(config)
            if success:
                self.control_panel.set_server_running(True)
                self.log_info(f"FTP服务器已启动 ({'多线程' if config['threading'] else '单线程'}模式)")
                
                # 添加视觉反馈动画
                self._animate_widget(self.control_panel, duration=500)
                return True
            else:
                self.log_error("启动服务器失败")
                QMessageBox.critical(self, "服务器错误", "启动服务器失败")
                return False
        except (ServerError, ValidationError) as e:
            self.log_error(f"启动服务器失败: {str(e)}")
            QMessageBox.critical(self, "服务器错误", f"启动服务器失败: {str(e)}")
            return False
        except Exception as e:
            self.log_error(f"启动服务器时发生未知错误: {str(e)}")
            QMessageBox.critical(self, "服务器错误", f"启动服务器时发生未知错误: {str(e)}")
            return False
    
    def stop_server(self):
        """Stop the FTP server."""
        if self.ftp_server_manager.is_running():
            try:
                success = self.ftp_server_manager.stop_server()
                if success:
                    self.control_panel.set_server_running(False)
                    self.log_info("FTP服务器已停止")
                    
                    # 添加视觉反馈动画
                    self._animate_widget(self.control_panel, duration=500)
                    return True
                else:
                    self.log_error("停止服务器失败")
                    return False
            except PyFTPError as e:
                self.log_error(f"停止服务器失败: {str(e)}")
                return False
        return True
    
    def toggle_server(self):
        """Toggle the FTP server on/off."""
        if self.ftp_server_manager.is_running():
            self.stop_server()
        else:
            self.start_server()
    
    def _animate_widget(self, widget, duration=300):
        """Add a visual animation to a widget."""
        try:
            # 创建透明度效果
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            
            # 创建动画
            animation = QPropertyAnimation(effect, b"opacity")
            animation.setDuration(duration)
            animation.setStartValue(0.3)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
        except Exception as e:
            # 静默处理动画错误，不影响主要功能
            pass
    
    def closeEvent(self, a0):
        """Handle window close event."""
        # 停止状态更新定时器
        self.status_update_timer.stop()
        
        # 清理日志处理器
        if hasattr(self, 'log_handler') and self.log_handler:
            # 从日志记录器中移除处理器
            root_logger = logging.getLogger()
            if self.log_handler in root_logger.handlers:
                root_logger.removeHandler(self.log_handler)
            
            # 关闭处理器
            self.log_handler.close()
            self.log_handler = None
        
        # 停止FTP服务器
        if self.ftp_server_manager.is_running():
            reply = QMessageBox.question(
                self, '确认退出', 'FTP服务器正在运行，确定要退出吗？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.stop_server()
                if success:
                    if a0:
                        a0.accept()
                else:
                    if a0:
                        a0.ignore()
                    # 重新启动状态更新定时器
                    self.status_update_timer.start(STATUS_UPDATE_INTERVAL)
            else:
                if a0:
                    a0.ignore()
                # 重新启动状态更新定时器
                self.status_update_timer.start(STATUS_UPDATE_INTERVAL)
        else:
            if a0:
                a0.accept()