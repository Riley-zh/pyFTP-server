"""
User panel for displaying user configuration information.
"""

from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel
)


class UserPanel(QGroupBox):
    """User panel for displaying user configuration information."""
    
    def __init__(self):
        super().__init__("用户配置")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user panel UI."""
        user_layout = QVBoxLayout()
        user_info = QHBoxLayout()
        user_info.addWidget(QLabel("当前配置: 匿名访问模式 (用户名: anonymous, 无密码)"))
        user_layout.addLayout(user_info)
        self.setLayout(user_layout)