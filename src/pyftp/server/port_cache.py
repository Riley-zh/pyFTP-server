"""
Port availability cache for PyFTP server.
"""

import socket
import threading
import time
from typing import Dict, Tuple

from pyftp.core.base_service import BaseService


class PortCache(BaseService):
    """Cache for port availability checks to improve performance."""
    
    def __init__(self, cache_ttl: int = 30):
        """
        Initialize the port cache.
        
        Args:
            cache_ttl: Time to live for cache entries in seconds
        """
        BaseService.__init__(self)
        self.cache_ttl = cache_ttl
        self._cache: Dict[Tuple[str, int], Tuple[bool, float]] = {}
        self._lock = threading.Lock()
    
    def is_port_available(self, port: int, host: str = "0.0.0.0") -> bool:
        """
        Check if a port is available, using cache when possible.
        
        Args:
            port: Port number to check
            host: Host address to bind to, defaults to "0.0.0.0"
            
        Returns:
            True if port is available, False otherwise
        """
        cache_key = (host, port)
        current_time = time.time()
        
        # Check cache first
        with self._lock:
            if cache_key in self._cache:
                is_available, timestamp = self._cache[cache_key]
                if current_time - timestamp < self.cache_ttl:
                    return is_available
                else:
                    # Remove expired entry
                    del self._cache[cache_key]
        
        # Perform actual check
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                is_available = True
        except OSError:
            is_available = False
        
        # Update cache
        with self._lock:
            self._cache[cache_key] = (is_available, current_time)
        
        return is_available
    
    def is_port_range_available(self, start: int, end: int, host: str = "0.0.0.0") -> bool:
        """
        Check if a range of ports is available, using cache when possible.
        
        Args:
            start: Start port number (inclusive)
            end: End port number (inclusive)
            host: Host address to bind to, defaults to "0.0.0.0"
            
        Returns:
            True if all ports in range are available, False otherwise
        """
        for port in range(start, end + 1):
            if not self.is_port_available(port, host):
                return False
        return True
    
    def clear_cache(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        current_time = time.time()
        with self._lock:
            expired_keys = [
                key for key, (_, timestamp) in self._cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            for key in expired_keys:
                del self._cache[key]


# Global port cache instance
_port_cache: PortCache | None = None
_port_cache_lock = threading.Lock()


def get_port_cache() -> PortCache:
    """Get or create global port cache instance."""
    global _port_cache
    with _port_cache_lock:
        if _port_cache is None:
            _port_cache = PortCache(cache_ttl=60)  # 增加缓存TTL到60秒以提高性能
        return _port_cache
