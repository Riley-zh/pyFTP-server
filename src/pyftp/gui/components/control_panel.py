"""
Control panel with action buttons for the FTP server.
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import pyqtSignal

from pyftp.core.qt_base_service import QtBaseService


class ControlPanel(QWidget, QtBaseService):
    """Control panel with action buttons."""
    
    # Signals
    server_state_changed = pyqtSignal(bool)
    config_saved = pyqtSignal()
    config_reloaded = pyqtSignal()
    log_cleared = pyqtSignal()
    
    def __init__(self):
        QWidget.__init__(self)
        QtBaseService.__init__(self)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the control panel UI."""
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("启动服务器")
        btn_layout.addWidget(self.start_btn)
        
        self.save_btn = QPushButton("保存配置")
        btn_layout.addWidget(self.save_btn)
        
        self.reload_btn = QPushButton("热重载配置")
        self.reload_btn.setEnabled(False)
        btn_layout.addWidget(self.reload_btn)
        
        self.clear_log_btn = QPushButton("清空日志")
        btn_layout.addWidget(self.clear_log_btn)
        
        self.setLayout(btn_layout)
    
    def set_server_running(self, running: bool):
        """Update UI state based on server running status."""
        if running:
            self.start_btn.setText("停止服务器")
            self.reload_btn.setEnabled(True)
        else:
            self.start_btn.setText("启动服务器")
            self.reload_btn.setEnabled(False)
        
        # 发送信号
        self.server_state_changed.emit(running)