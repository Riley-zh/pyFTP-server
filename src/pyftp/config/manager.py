"""
Configuration manager for loading and saving server settings.
"""

import os
import configparser
import time
from typing import Dict, Any, Optional
from pathlib import Path

from pyftp.core.base_service import BaseService
from pyftp.core.interfaces import ConfigManager as ConfigManagerInterface
from pyftp.core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END, 
    DEFAULT_ENCODING_IDX, DEFAULT_THREADING_IDX,
    MIN_PORT, MAX_PORT, MIN_PASSIVE_PORT, MAX_PASSIVE_PORT
)
from pyftp.core.exceptions import ConfigError
from pyftp.core.error_handler import handle_errors, get_error_details
from pyftp.utils.helpers import validate_directory


class ConfigManager(BaseService, ConfigManagerInterface):
    """Manager for loading and saving configuration."""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'port': DEFAULT_PORT,
        'directory': DEFAULT_DIRECTORY,
        'passive': DEFAULT_PASSIVE_MODE,
        'passive_start': DEFAULT_PASSIVE_START,
        'passive_end': DEFAULT_PASSIVE_END,
        'encoding_idx': DEFAULT_ENCODING_IDX,
        'threading_idx': DEFAULT_THREADING_IDX
    }
    
    def __init__(self, config_file: str = "ftpserver.ini"):
        BaseService.__init__(self)
        self.config_file = Path(config_file).resolve()
        self._config_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 30  # 增加缓存时间到30秒以提高性能
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Returns:
            Dict with configuration data or None if file doesn't exist
            
        Raises:
            ConfigError: If there's an error parsing the configuration file
        """
        # 检查缓存
        current_time = time.time()
        if self._config_cache is not None and (current_time - self._cache_timestamp) < self._cache_ttl:
            return self._config_cache
            
        if not self.config_file.exists():
            self.log_info(f"配置文件不存在: {self.config_file}")
            self._config_cache = None
            self._cache_timestamp = current_time
            return None
            
        config = configparser.ConfigParser()
        
        try:
            # 检查文件是否可读
            if not os.access(self.config_file, os.R_OK):
                self.log_warning(f"配置文件无法读取: {self.config_file}")
                self._config_cache = None
                self._cache_timestamp = current_time
                return None
                
            config.read(self.config_file, encoding='utf-8')
            
            if config.has_section('server'):
                config_data = {}
                # 从默认配置开始，然后用文件中的值覆盖
                config_data.update(self.DEFAULT_CONFIG)
                
                # 正确处理编码和线程模式的加载
                encoding_value = config.get('server', 'encoding_idx', fallback=str(self.DEFAULT_CONFIG['encoding_idx']))
                threading_value = config.get('server', 'threading_idx', fallback=str(self.DEFAULT_CONFIG['threading_idx']))
                
                config_data.update({
                    'port': config.getint('server', 'port', fallback=self.DEFAULT_CONFIG['port']),
                    'directory': config.get('server', 'directory', fallback=self.DEFAULT_CONFIG['directory']),
                    'passive': config.getboolean('server', 'passive', fallback=self.DEFAULT_CONFIG['passive']),
                    'passive_start': config.getint('server', 'passive_start', fallback=self.DEFAULT_CONFIG['passive_start']),
                    'passive_end': config.getint('server', 'passive_end', fallback=self.DEFAULT_CONFIG['passive_end']),
                    'encoding_idx': self._parse_int_value(encoding_value, self.DEFAULT_CONFIG['encoding_idx']),
                    'threading_idx': self._parse_int_value(threading_value, self.DEFAULT_CONFIG['threading_idx'])
                })
                self.log_info(f"配置文件加载成功: {self.config_file}")
                # 更新缓存
                self._config_cache = config_data
                self._cache_timestamp = current_time
                return config_data
            else:
                self.log_warning(f"配置文件缺少'server'节: {self.config_file}")
                self._config_cache = None
                self._cache_timestamp = current_time
                return None
        except configparser.Error as e:
            self.log_error(f"解析配置文件失败: {str(e)}")
            self._config_cache = None
            self._cache_timestamp = current_time
            raise ConfigError(f"解析配置文件失败: {str(e)}")
        except Exception as e:
            self.log_error(f"加载配置失败: {str(e)}")
            self._config_cache = None
            self._cache_timestamp = current_time
            raise ConfigError(f"加载配置失败: {str(e)}")
    
    def _parse_int_value(self, value: str, default: int) -> int:
        """Parse string value to int, handling both string and int representations."""
        try:
            # 如果是数字字符串，直接转换
            if isinstance(value, str) and (value.isdigit() or (value.startswith('-') and value[1:].isdigit())):
                return int(value)
            # 其他情况返回默认值
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    @handle_errors(default_return=False, log_errors=True)
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config_data: Dictionary with configuration data
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ConfigError: If there's an error saving the configuration file
        """
        # 验证配置数据
        self._validate_config(config_data)
        
        config = configparser.ConfigParser()
        
        try:
            config.add_section('server')
            
            # 保存所有配置项
            for key, value in config_data.items():
                # 特殊处理编码和线程模式索引
                if key in ['encoding_idx', 'threading_idx']:
                    config.set('server', key, str(value))
                elif key == 'encoding':
                    # 保存编码索引而不是编码字符串
                    encoding_idx = config_data.get('encoding_idx', 0)
                    config.set('server', 'encoding_idx', str(encoding_idx))
                elif key == 'threading':
                    # 保存线程模式索引而不是布尔值
                    threading_idx = config_data.get('threading_idx', 1)
                    config.set('server', 'threading_idx', str(threading_idx))
                elif isinstance(value, bool):
                    config.set('server', key, str(value).lower())
                else:
                    config.set('server', key, str(value))
            
            # 确保配置文件目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查文件是否可写
            if self.config_file.exists() and not os.access(self.config_file, os.W_OK):
                self.log_error(f"配置文件无法写入: {self.config_file}")
                return False
                
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            self.log_info(f"配置文件保存成功: {self.config_file}")
            # 清除缓存以强制重新加载
            self._config_cache = None
            return True
        except Exception as e:
            error_details = get_error_details(e)
            self.log_error(f"保存配置失败: {str(e)} - 详细信息: {error_details}")
            raise ConfigError(f"保存配置失败: {str(e)}", error_code="CFG002", details=error_details)
    
    def _validate_config(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration data.
        
        Args:
            config_data: Configuration data to validate
            
        Raises:
            ConfigError: If validation fails
        """
        if not config_data:
            raise ConfigError("配置数据不能为空")
            
        # 验证端口
        port = config_data.get('port', DEFAULT_PORT)
        if not isinstance(port, int) or not (MIN_PORT <= port <= MAX_PORT):
            raise ConfigError(f"端口必须是 {MIN_PORT}-{MAX_PORT} 范围内的整数")
            
        # 验证目录
        directory = config_data.get('directory', DEFAULT_DIRECTORY)
        if not validate_directory(directory):
            raise ConfigError(f"目录不存在或无法访问: {directory}")
            
        # 验证被动模式设置
        if config_data.get('passive', DEFAULT_PASSIVE_MODE):
            passive_start = config_data.get('passive_start', DEFAULT_PASSIVE_START)
            passive_end = config_data.get('passive_end', DEFAULT_PASSIVE_END)
            
            if not isinstance(passive_start, int) or not (MIN_PASSIVE_PORT <= passive_start <= MAX_PASSIVE_PORT):
                raise ConfigError(f"被动起始端口必须是 {MIN_PASSIVE_PORT}-{MAX_PASSIVE_PORT} 范围内的整数")
                
            if not isinstance(passive_end, int) or not (MIN_PASSIVE_PORT <= passive_end <= MAX_PASSIVE_PORT):
                raise ConfigError(f"被动结束端口必须是 {MIN_PASSIVE_PORT}-{MAX_PASSIVE_PORT} 范围内的整数")
                
            if passive_start >= passive_end:
                raise ConfigError("被动端口范围无效: 起始端口必须小于结束端口")
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values and save to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.save_config(self.DEFAULT_CONFIG)
        except ConfigError:
            return False
    
    def get_config_path(self) -> Path:
        """Get the configuration file path.
        
        Returns:
            Path to the configuration file
        """
        return self.config_file