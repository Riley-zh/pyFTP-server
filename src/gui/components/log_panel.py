"""
Log panel for displaying server logs.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QScrollBar
)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat

from core.qt_base_service import QtBaseService
from core.constants import LOG_LEVEL_ALL, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, MAX_LOG_LINES
from PyQt5.QtCore import QTimer


class GuiLogPanel(QGroupBox, QtBaseService):
    """Log panel for displaying server logs."""
    
    def __init__(self):
        QGroupBox.__init__(self, "服务器日志")
        QtBaseService.__init__(self)
        self.log_buffer = []
        self.max_lines = MAX_LOG_LINES
        self.batch_update_timer = None
        self.batch_size = 50
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the log panel UI."""
        log_layout = QVBoxLayout()
        
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
        
        self.log_view.setStyleSheet("background-color: black; color: white;")
        
        self.log_view.setLineWrapMode(QTextEdit.NoWrap)
        self.log_view.setAcceptRichText(False)
        
        log_layout.addWidget(self.log_view)
        self.setLayout(log_layout)
    
    def append_log(self, message, level):
        """Append a log message with color coding."""
        self.log_buffer.append((message, level))
        
        if len(self.log_buffer) >= self.batch_size or level in ["ERROR", "CRITICAL"]:
            self._process_log_buffer()
        elif level == "WARNING":
            if not hasattr(self, '_buffer_timer'):
                self._buffer_timer = QTimer()
                self._buffer_timer.setSingleShot(True)
                self._buffer_timer.timeout.connect(self._process_log_buffer)
            self._buffer_timer.stop()
            self._buffer_timer.start(200)
        else:
            if not hasattr(self, '_buffer_timer'):
                self._buffer_timer = QTimer()
                self._buffer_timer.setSingleShot(True)
                self._buffer_timer.timeout.connect(self._process_log_buffer)
            self._buffer_timer.stop()
            self._buffer_timer.start(500)
    
    def _process_log_buffer(self):
        """Process the log buffer in batches for better performance."""
        if not self.log_buffer:
            return
        
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = False
        if scrollbar:
            at_bottom = scrollbar.value() == scrollbar.maximum()
        
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)
        
        format = QTextCharFormat()
        
        for message, level in self.log_buffer:
            # 根据日志级别设置颜色（符合常见日志显示惯例）
            if level == "WARNING":
                color = QColor("yellow")  # 黄色
            elif level == "ERROR" or level == "CRITICAL":
                color = QColor("red")  # 红色
            elif level == "INFO":
                color = QColor("green")  # 绿色
            else:
                color = QColor("white")  # 白色
            
            format.setForeground(color)
            cursor.setCharFormat(format)
            cursor.insertText(message + '\n')
        
        self.log_buffer.clear()
        
        self._limit_log_lines()
        
        if at_bottom and scrollbar:
            scrollbar.setValue(scrollbar.maximum())
    
    def _limit_log_lines(self):
        """Limit the number of log lines to prevent memory issues."""
        doc = self.log_view.document()
        if doc:
            line_count = doc.blockCount()
            
            if line_count > self.max_lines:
                cursor = self.log_view.textCursor()
                cursor.movePosition(QTextCursor.Start)
                cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, line_count - self.max_lines)
                cursor.removeSelectedText()
    
    def filter_logs(self):
        """Filter logs based on selected level."""
        level_index = self.log_level_combo.currentIndex()
        level_map = {0: None, 1: "INFO", 2: "WARNING", 3: "ERROR"}
        filter_level = level_map[level_index]
        
        scrollbar = self.log_view.verticalScrollBar()
        scroll_value = scrollbar.value() if scrollbar else 0
        
        full_text = self.log_view.toPlainText()
        lines = full_text.split('\n')
        
        self.log_view.clear()
        
        cursor = self.log_view.textCursor()
        format = QTextCharFormat()
        
        for line in lines:
            if not line:
                continue
                
            should_show = True
            if filter_level is not None:
                if filter_level == "INFO" and " INFO:" not in line:
                    should_show = False
                elif filter_level == "WARNING" and " WARNING:" not in line:
                    should_show = False
                elif filter_level == "ERROR" and not (" ERROR:" in line or " CRITICAL:" in line):
                    should_show = False
            
            if should_show:
                if " WARNING:" in line:
                    color = QColor("yellow")
                elif " ERROR:" in line or " CRITICAL:" in line:
                    color = QColor("red")
                elif " INFO:" in line:
                    color = QColor("green")
                else:
                    color = QColor("white")
                
                format.setForeground(color)
                cursor.setCharFormat(format)
                cursor.insertText(line + '\n')
        
        if scrollbar:
            scrollbar.setValue(min(scroll_value, scrollbar.maximum()))
        
        self.log_view.moveCursor(QTextCursor.End)
    
    def clear_log(self):
        """Clear the log display."""
        if hasattr(self, '_buffer_timer') and self._buffer_timer.isActive():
            self._buffer_timer.stop()
        
        self.log_view.clear()
        self.log_buffer.clear()