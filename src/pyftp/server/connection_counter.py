"""
Connection counter for tracking active FTP connections.
"""
import os
import json
import threading
import time
from pathlib import Path
from typing import Optional
import logging

class ConnectionCounter:
    """Thread-safe connection counter that persists to file."""
    
    def __init__(self, counter_file: str = "connection_count.json"):
        self.counter_file = Path(counter_file)
        self._count = 0
        self._lock = threading.Lock()
        self._load_count()
    
    def _load_count(self) -> None:
        """Load connection count from file."""
        try:
            if self.counter_file.exists():
                with open(self.counter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._count = data.get('count', 0)
        except Exception as e:
            logging.warning(f"无法加载连接计数文件: {e}")
            self._count = 0
    
    def _save_count(self) -> None:
        """Save connection count to file."""
        try:
            with open(self.counter_file, 'w', encoding='utf-8') as f:
                json.dump({'count': self._count, 'timestamp': time.time()}, f)
        except Exception as e:
            logging.error(f"无法保存连接计数文件: {e}")
    
    def increment(self) -> None:
        """Increment connection count."""
        with self._lock:
            self._count += 1
            self._save_count()
    
    def decrement(self) -> None:
        """Decrement connection count."""
        with self._lock:
            self._count = max(0, self._count - 1)
            self._save_count()
    
    def get_count(self) -> int:
        """Get current connection count."""
        with self._lock:
            return self._count
    
    def reset(self) -> None:
        """Reset connection count to zero."""
        with self._lock:
            self._count = 0
            self._save_count()


# 全局连接计数器实例
connection_counter: Optional[ConnectionCounter] = None
counter_lock = threading.Lock()


def get_connection_counter() -> ConnectionCounter:
    """Get or create global connection counter instance."""
    global connection_counter
    with counter_lock:
        if connection_counter is None:
            connection_counter = ConnectionCounter()
        return connection_counter