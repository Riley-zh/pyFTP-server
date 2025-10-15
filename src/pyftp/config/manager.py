"""
Configuration manager for loading and saving server settings.
"""

import os
import configparser
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from pyftp.core.interfaces import ConfigManager as ConfigManagerInterface
from pyftp.core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END, 
    DEFAULT_ENCODING_IDX, DEFAULT_THREADING_IDX
)


class ConfigManager(ConfigManagerInterface):
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
        self.config_file = Path(config_file).resolve()
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Returns:
            Dict with configuration data or None if file doesn't exist
        """
        if not self.config_file.exists():
            logging.info(f"配置文件不存在: {self.config_file}")
            return None
            
        config = configparser.ConfigParser()
        
        try:
            # 检查文件是否可读
            if not os.access(self.config_file, os.R_OK):
                logging.warning(f"配置文件无法读取: {self.config_file}")
                return None
                
            config.read(self.config_file, encoding='utf-8')
            
            if config.has_section('server'):
                config_data = {}
                # 从默认配置开始，然后用文件中的值覆盖
                config_data.update(self.DEFAULT_CONFIG)
                
                # 正确处理编码和线程模式的加载
                encoding_value = config.get('server', 'encoding', fallback=str(self.DEFAULT_CONFIG['encoding_idx']))
                threading_value = config.get('server', 'threading', fallback=str(self.DEFAULT_CONFIG['threading_idx']))
                
                config_data.update({
                    'port': config.getint('server', 'port', fallback=self.DEFAULT_CONFIG['port']),
                    'directory': config.get('server', 'directory', fallback=self.DEFAULT_CONFIG['directory']),
                    'passive': config.getboolean('server', 'passive', fallback=self.DEFAULT_CONFIG['passive']),
                    'passive_start': config.getint('server', 'passive_start', fallback=self.DEFAULT_CONFIG['passive_start']),
                    'passive_end': config.getint('server', 'passive_end', fallback=self.DEFAULT_CONFIG['passive_end']),
                    'encoding_idx': self._parse_int_value(encoding_value, self.DEFAULT_CONFIG['encoding_idx']),
                    'threading_idx': self._parse_int_value(threading_value, self.DEFAULT_CONFIG['threading_idx'])
                })
                logging.info(f"配置文件加载成功: {self.config_file}")
                return config_data
            else:
                logging.warning(f"配置文件缺少'server'节: {self.config_file}")
                return None
        except configparser.Error as e:
            logging.error(f"解析配置文件失败: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            return None
    
    def _parse_int_value(self, value: str, default: int) -> int:
        """Parse string value to int, handling both string and int representations."""
        try:
            # 如果是数字字符串，直接转换
            if isinstance(value, str) and (value.isdigit() or (value.startswith('-') and value[1:].isdigit())):
                return int(value)
            # 如果是编码字符串（'gbk'或'utf-8'），则根据内容返回索引
            elif isinstance(value, str) and value.lower() == 'gbk':
                return 0
            elif isinstance(value, str) and value.lower() == 'utf-8':
                return 1
            # 其他情况返回默认值
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config_data: Dictionary with configuration data
            
        Returns:
            True if successful, False otherwise
        """
        config = configparser.ConfigParser()
        
        try:
            config.add_section('server')
            
            # 保存所有配置项，而不仅仅是与默认值不同的项
            # 这样可以确保配置文件包含完整的配置信息
            for key, value in config_data.items():
                # 对于编码和线程模式，确保保存索引值而不是字符串值
                if key == 'encoding':
                    # 将编码字符串转换为索引
                    if value == 'gbk':
                        config.set('server', 'encoding', '0')
                    elif value == 'utf-8':
                        config.set('server', 'encoding', '1')
                    else:
                        config.set('server', 'encoding', str(value))
                elif key == 'threading':
                    # 将布尔值转换为索引
                    config.set('server', 'threading', '1' if value else '0')
                elif isinstance(value, bool):
                    config.set('server', key, str(value).lower())
                else:
                    config.set('server', key, str(value))
            
            # 确保配置文件目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查文件是否可写
            if self.config_file.exists() and not os.access(self.config_file, os.W_OK):
                logging.error(f"配置文件无法写入: {self.config_file}")
                return False
                
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            logging.info(f"配置文件保存成功: {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values and save to file.
        
        Returns:
            True if successful, False otherwise
        """
        return self.save_config(self.DEFAULT_CONFIG)
    
    def get_config_path(self) -> Path:
        """Get the configuration file path.
        
        Returns:
            Path to the configuration file
        """
        return self.config_file