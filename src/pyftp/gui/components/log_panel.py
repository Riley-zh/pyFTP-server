"""
Log panel for displaying server logs.
"""

from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QComboBox, QScrollBar
)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat


class LogPanel(QGroupBox):
    """Log panel for displaying server logs."""
    
    def __init__(self):
        super().__init__("服务器日志")
        self.log_buffer = []  # 缓冲区用于批量更新
        self.max_lines = 5000  # 限制最大日志行数
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
        
        # 优化性能：禁用换行和自动滚动
        self.log_view.setLineWrapMode(QTextEdit.NoWrap)
        self.log_view.setAcceptRichText(False)
        
        log_layout.addWidget(self.log_view)
        self.setLayout(log_layout)
    
    def append_log(self, message, level):
        """Append a log message with color coding."""
        # 添加到缓冲区
        self.log_buffer.append((message, level))
        
        # 如果缓冲区达到一定大小，或者这是重要的日志级别，立即处理
        if len(self.log_buffer) >= 10 or level in ["ERROR", "CRITICAL", "WARNING"]:
            self._process_log_buffer()
        # 对于INFO级别的日志，也定期处理以确保显示
        elif len(self.log_buffer) > 0:
            # 使用单次定时器来处理缓冲区，避免频繁调用
            if not hasattr(self, '_buffer_timer'):
                from PyQt5.QtCore import QTimer
                self._buffer_timer = QTimer()
                self._buffer_timer.setSingleShot(True)
                self._buffer_timer.timeout.connect(self._process_log_buffer)
            # 重启定时器，延迟100毫秒处理
            self._buffer_timer.start(100)
    
    def _process_log_buffer(self):
        """Process the log buffer in batches for better performance."""
        if not self.log_buffer:
            return
        
        # 保存当前滚动位置
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # 批量处理日志
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_view.setTextCursor(cursor)
        
        format = QTextCharFormat()
        
        for message, level in self.log_buffer:
            if level == "WARNING":
                color = "#FFA500"
            elif level == "ERROR" or level == "CRITICAL":
                color = "#FF5555"
            elif level == "INFO":
                color = "#55AAFF"
            else:
                color = "#DCDCDC"
            
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
            cursor.insertText(message + '\n')
        
        # 清空缓冲区
        self.log_buffer.clear()
        
        # 限制日志行数
        self._limit_log_lines()
        
        # 恢复滚动位置
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def _limit_log_lines(self):
        """Limit the number of log lines to prevent memory issues."""
        doc = self.log_view.document()
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
        self.log_buffer.clear()