"""
Log panel for displaying server logs.
"""

from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QTextCursor


class LogPanel(QGroupBox):
    """Log panel for displaying server logs."""
    
    def __init__(self):
        super().__init__("服务器日志")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the log panel UI."""
        log_layout = QVBoxLayout()
        
        # 日志级别过滤
        log_filter_layout = QHBoxLayout()
        log_filter_layout.addWidget(QLabel("日志级别:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["全部", "信息", "警告", "错误"])
        self.log_level_combo.setCurrentIndex(0)
        log_filter_layout.addWidget(self.log_level_combo)
        log_filter_layout.addStretch()
        log_layout.addLayout(log_filter_layout)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                font-family: Consolas, Courier New, monospace;
                font-size: 10pt;
            }
        """)
        log_layout.addWidget(self.log_view)
        self.setLayout(log_layout)
    
    def append_log(self, message, level):
        """Append a log message with color coding."""
        if level == "WARNING":
            color = "#FFA500"
        elif level == "ERROR" or level == "CRITICAL":
            color = "#FF5555"
        elif level == "INFO":
            color = "#55AAFF"
        else:
            color = "#DCDCDC"
        
        # 保存当前滚动位置
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # 添加带颜色的日志
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.setTextColor(QColor(color))
        self.log_view.insertPlainText(message + '\n')
        
        # 恢复滚动位置
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def filter_logs(self):
        """Filter logs based on selected level."""
        level_index = self.log_level_combo.currentIndex()
        level_map = {0: None, 1: "INFO", 2: "WARNING", 3: "ERROR"}
        filter_level = level_map[level_index]
        
        # 获取所有日志内容
        full_text = self.log_view.toPlainText()
        lines = full_text.split('\n')
        
        # 清空并重新添加过滤后的日志
        self.log_view.clear()
        
        for line in lines:
            if not line:
                continue
                
            if filter_level is None or f" {filter_level}:" in line:
                if " WARNING:" in line:
                    color = "#FFA500"
                elif " ERROR:" in line or " CRITICAL:" in line:
                    color = "#FF5555"
                elif " INFO:" in line:
                    color = "#55AAFF"
                else:
                    color = "#DCDCDC"
                
                self.log_view.setTextColor(QColor(color))
                self.log_view.append(line)
        
        # 滚动到底部
        self.log_view.moveCursor(QTextCursor.End)
    
    def clear_log(self):
        """Clear the log display."""
        self.log_view.clear()