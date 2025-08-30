"""
Control panel with action buttons for the FTP server.
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton
)


class ControlPanel(QWidget):
    """Control panel with action buttons."""
    
    def __init__(self):
        super().__init__()
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