"""
Unit tests for the configuration manager.
"""

import os
import unittest
import tempfile
import shutil
from pyftp.config.manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for the ConfigManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.ini")
        self.config_manager = ConfigManager(self.config_file)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        # Test data
        config_data = {
            'port': 2121,
            'directory': '/tmp',
            'passive': True,
            'passive_start': 60000,
            'passive_end': 61000,
            'encoding_idx': 0,
            'threading_idx': 1
        }
        
        # Save config
        result = self.config_manager.save_config(config_data)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load config
        loaded_config = self.config_manager.load_config()
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config['port'], config_data['port'])
        self.assertEqual(loaded_config['directory'], config_data['directory'])
        self.assertEqual(loaded_config['passive'], config_data['passive'])
        self.assertEqual(loaded_config['passive_start'], config_data['passive_start'])
        self.assertEqual(loaded_config['passive_end'], config_data['passive_end'])
        self.assertEqual(loaded_config['encoding_idx'], config_data['encoding_idx'])
        self.assertEqual(loaded_config['threading_idx'], config_data['threading_idx'])
    
    def test_load_nonexistent_config(self):
        """Test loading configuration when file doesn't exist."""
        # Use a non-existent file
        nonexistent_manager = ConfigManager("nonexistent.ini")
        config = nonexistent_manager.load_config()
        self.assertIsNone(config)


if __name__ == '__main__':
    unittest.main()