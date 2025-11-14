"""
Custom logging handler for displaying logs in the GUI.
"""

import logging
import threading
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal

from pyftp.core.base_service import BaseService


class QtLogHandler(QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for GUI updates."""
    
    log_signal = pyqtSignal(str, str)
    
    def __init__(self, max_buffer_size: int = 1000):
        # 由于多重继承，直接调用父类初始化
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', 
                                           datefmt='%Y-%m-%d %H:%M:%S'))
        
        # 使用缓冲区来减少UI更新频率
        self.buffer = deque(maxlen=max_buffer_size)
        self.buffer_lock = threading.Lock()
        
        # 标记对象是否已被清理
        self._closed = False
    
    def emit(self, record):
        """Emit a log record as a Qt signal."""
        # 检查对象是否已被清理
        if self._closed:
            return
            
        try:
            msg = self.format(record)
            level = record.levelname
            
            # 将日志添加到缓冲区
            with self.buffer_lock:
                self.buffer.append((msg, level))
            
            # 立即发送信号，不使用定时器
            self.log_signal.emit(msg, level)
        except Exception as e:
            # 只在调试时打印错误，避免在关闭时产生干扰
            pass
    
    def flush(self):
        """Flush the handler's buffer."""
        pass
    
    def close(self):
        """Clean up resources."""
        self._closed = True
        
        # 清空缓冲区
        with self.buffer_lock:
            self.buffer.clear()
            
        # 调用父类的close方法
        super().close()