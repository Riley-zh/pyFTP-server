"""
Configuration manager for loading and saving server settings.
"""

import os
import configparser
import logging


class ConfigManager:
    """Manager for loading and saving configuration."""
    
    def __init__(self, config_file="ftpserver.ini"):
        self.config_file = config_file
    
    def load_config(self):
        """Load configuration from file."""
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file, encoding='utf-8')
                
                if config.has_section('server'):
                    config_data = {
                        'port': config.getint('server', 'port', fallback=2121),
                        'directory': config.get('server', 'directory', fallback=os.getcwd()),
                        'passive': config.getboolean('server', 'passive', fallback=True),
                        'passive_start': config.getint('server', 'passive_start', fallback=60000),
                        'passive_end': config.getint('server', 'passive_end', fallback=61000),
                        'encoding_idx': config.getint('server', 'encoding', fallback=0),
                        'threading_idx': config.getint('server', 'threading', fallback=1)
                    }
                    return config_data
            except Exception as e:
                logging.error(f"加载配置失败: {str(e)}")
        return None
    
    def save_config(self, config_data):
        """Save configuration to file."""
        config = configparser.ConfigParser()
        
        config.add_section('server')
        try:
            config.set('server', 'port', str(config_data['port']))
            config.set('server', 'directory', config_data['directory'])
            config.set('server', 'passive', str(config_data['passive']))
            config.set('server', 'passive_start', str(config_data['passive_start']))
            config.set('server', 'passive_end', str(config_data['passive_end']))
            config.set('server', 'encoding', str(config_data.get('encoding_idx', 0) if 'encoding_idx' in config_data else (0 if config_data['encoding'] == 'gbk' else 1)))
            config.set('server', 'threading', str(config_data.get('threading_idx', 1) if 'threading_idx' in config_data else (1 if config_data['threading'] else 0)))
            
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            return False