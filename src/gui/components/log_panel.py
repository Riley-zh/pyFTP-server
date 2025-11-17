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
        self.log_buffer = []  # 缓冲区用于批量更新
        self.max_lines = MAX_LOG_LINES  # 限制最大日志行数
        self.batch_update_timer = None  # 批量更新定时器
        self.batch_size = 50  # 增加批处理大小以提高性能
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
        
        # 优化性能：禁用换行和自动滚动
        self.log_view.setLineWrapMode(QTextEdit.NoWrap)
        self.log_view.setAcceptRichText(False)
        
        log_layout.addWidget(self.log_view)
        self.setLayout(log_layout)
    
    def append_log(self, message, level):
        """Append a log message with color coding."""
        # 添加到缓冲区
        self.log_buffer.append((message, level))
        
        # 增加批处理大小阈值以提高性能
        if len(self.log_buffer) >= self.batch_size or level in ["ERROR", "CRITICAL"]:
            self._process_log_buffer()
        # 对于WARNING级别的日志，定期处理
        elif level == "WARNING":
            # 使用单次定时器来处理缓冲区，避免频繁调用
            if not hasattr(self, '_buffer_timer'):
                self._buffer_timer = QTimer()
                self._buffer_timer.setSingleShot(True)
                self._buffer_timer.timeout.connect(self._process_log_buffer)
            # 重启定时器，延迟200毫秒处理
            self._buffer_timer.stop()
            self._buffer_timer.start(200)
        # 对于INFO级别的日志，延长处理时间以提高性能
        else:
            # 使用单次定时器来处理缓冲区，避免频繁调用
            if not hasattr(self, '_buffer_timer'):
                self._buffer_timer = QTimer()
                self._buffer_timer.setSingleShot(True)
                self._buffer_timer.timeout.connect(self._process_log_buffer)
            # 重启定时器，延迟500毫秒处理
            self._buffer_timer.stop()
            self._buffer_timer.start(500)
    
    def _process_log_buffer(self):
        """Process the log buffer in batches for better performance."""
        if not self.log_buffer:
            return
        
        # 保存当前滚动位置
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = False
        if scrollbar:
            at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # 批量处理日志
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)
        
        format = QTextCharFormat()
        
        for message, level in self.log_buffer:
            # 根据日志级别设置颜色
            if level == "WARNING":
                color = QColor("#FFA500")  # 橙色
            elif level == "ERROR" or level == "CRITICAL":
                color = QColor("#FF5555")  # 红色
            elif level == "INFO":
                color = QColor("#55AAFF")  # 蓝色
            else:
                color = QColor("#DCDCDC")  # 灰色
            
            format.setForeground(color)
            cursor.setCharFormat(format)
            cursor.insertText(message + '\n')
        
        # 清空缓冲区
        self.log_buffer.clear()
        
        # 限制日志行数
        self._limit_log_lines()
        
        # 恢复滚动位置
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
        
        # 保存当前滚动位置
        scrollbar = self.log_view.verticalScrollBar()
        scroll_value = scrollbar.value() if scrollbar else 0
        
        # 获取所有文本
        full_text = self.log_view.toPlainText()
        lines = full_text.split('\n')
        
        # 清空视图
        self.log_view.clear()
        
        cursor = self.log_view.textCursor()
        format = QTextCharFormat()
        
        for line in lines:
            if not line:
                continue
                
            # 检查是否应该显示此行
            should_show = True
            if filter_level is not None:
                if filter_level == "INFO" and " INFO:" not in line:
                    should_show = False
                elif filter_level == "WARNING" and " WARNING:" not in line:
                    should_show = False
                elif filter_level == "ERROR" and not (" ERROR:" in line or " CRITICAL:" in line):
                    should_show = False
            
            if should_show:
                # 根据日志内容确定级别并设置颜色
                if " WARNING:" in line:
                    color = QColor("#FFA500")  # 橙色
                elif " ERROR:" in line or " CRITICAL:" in line:
                    color = QColor("#FF5555")  # 红色
                elif " INFO:" in line:
                    color = QColor("#55AAFF")  # 蓝色
                else:
                    color = QColor("#DCDCDC")  # 灰色
                
                format.setForeground(color)
                cursor.setCharFormat(format)
                cursor.insertText(line + '\n')
        
        # 恢复滚动位置
        if scrollbar:
            scrollbar.setValue(min(scroll_value, scrollbar.maximum()))
        
        # 滚动到底部
        self.log_view.moveCursor(QTextCursor.End)
    
    def clear_log(self):
        """Clear the log display."""
        # 停止可能正在运行的定时器
        if hasattr(self, '_buffer_timer') and self._buffer_timer.isActive():
            self._buffer_timer.stop()
        
        self.log_view.clear()
        self.log_buffer.clear()