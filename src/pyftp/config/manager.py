"""
Configuration manager for loading and saving server settings.
"""

import os
import configparser
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """Manager for loading and saving configuration."""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'port': 2121,
        'directory': os.getcwd(),
        'passive': True,
        'passive_start': 60000,
        'passive_end': 61000,
        'encoding_idx': 0,
        'threading_idx': 1
    }
    
    def __init__(self, config_file: str = "ftpserver.ini"):
        self.config_file = config_file
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Returns:
            Dict with configuration data or None if file doesn't exist
        """
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            try:
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
                    return config_data
            except Exception as e:
                logging.error(f"加载配置失败: {str(e)}")
        return None
    
    def _parse_int_value(self, value: str, default: int) -> int:
        """Parse string value to int, handling both string and int representations."""
        try:
            # 如果是数字字符串，直接转换
            if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                return int(value)
            # 如果是编码字符串（'gbk'或'utf-8'），则根据内容返回索引
            elif value.lower() == 'gbk':
                return 0
            elif value.lower() == 'utf-8':
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
        
        config.add_section('server')
        try:
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
            
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            return False