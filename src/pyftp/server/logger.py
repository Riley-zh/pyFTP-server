"""
Custom logging handler for displaying logs in the GUI.
"""

import logging
import threading
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class QtLogHandler(QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for GUI updates."""
    
    log_signal = pyqtSignal(str, str)
    
    def __init__(self, max_buffer_size: int = 1000):
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', 
                                           datefmt='%Y-%m-%d %H:%M:%S'))
        
        # 使用缓冲区来减少UI更新频率
        self.buffer = deque(maxlen=max_buffer_size)
        self.buffer_lock = threading.Lock()
        self.last_emit_time = 0
        self.emit_interval = 0.1  # 最小发送间隔（秒）
        
        # 定时器用于批量处理日志
        self.batch_timer = QTimer()
        self.batch_timer.timeout.connect(self._emit_buffer)
        self.batch_timer.setSingleShot(True)
    
    def emit(self, record):
        """Emit a log record as a Qt signal."""
        try:
            msg = self.format(record)
            level = record.levelname
            
            # 将日志添加到缓冲区
            with self.buffer_lock:
                self.buffer.append((msg, level))
            
            # 如果定时器没有运行，则启动它
            if not self.batch_timer.isActive():
                self.batch_timer.start(int(self.emit_interval * 1000))
        except Exception as e:
            print(f"Error in QtLogHandler.emit: {e}")  # 调试信息
            pass  # 忽略日志处理中的错误，避免影响主程序
    
    def _emit_buffer(self):
        """Emit all buffered log records."""
        try:
            with self.buffer_lock:
                if self.buffer:
                    # 发送所有缓冲的日志
                    for msg, level in self.buffer:
                        self.log_signal.emit(msg, level)
                    self.buffer.clear()
        except Exception as e:
            print(f"Error in QtLogHandler._emit_buffer: {e}")  # 调试信息
            pass  # 忽略日志处理中的错误，避免影响主程序