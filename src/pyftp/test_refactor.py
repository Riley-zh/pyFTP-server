"""
Test script to verify the refactored PyFTP server functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pyftp.config.manager import ConfigManager
from pyftp.server.ftp_server import FTPServerManager
from pyftp.application import PyFTPApplication


def test_config_manager():
    """Test configuration manager functionality."""
    print("Testing ConfigManager...")
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    config_file = os.path.join(test_dir, "test_config.ini")
    
    try:
        # Create config manager
        config_manager = ConfigManager(config_file)
        
        # Test saving config
        test_config = {
            'port': 2121,
            'directory': test_dir,
            'passive': True,
            'passive_start': 60000,
            'passive_end': 61000,
            'encoding_idx': 0,
            'threading_idx': 1
        }
        
        success = config_manager.save_config(test_config)
        assert success, "Failed to save configuration"
        print("  ✓ Save configuration: PASSED")
        
        # Test loading config
        loaded_config = config_manager.load_config()
        assert loaded_config is not None, "Failed to load configuration"
        assert loaded_config['port'] == 2121, "Port mismatch"
        assert loaded_config['directory'] == test_dir, "Directory mismatch"
        print("  ✓ Load configuration: PASSED")
        
        # Test config path
        config_path = config_manager.get_config_path()
        # Convert both paths to the same format for comparison
        expected_path = Path(config_file).resolve()
        actual_path = config_path.resolve()
        assert actual_path == expected_path, f"Config path mismatch: expected {expected_path}, got {actual_path}"
        print("  ✓ Get config path: PASSED")
        
        print("ConfigManager tests: PASSED")
        return True
        
    except Exception as e:
        print(f"ConfigManager tests: FAILED - {str(e)}")
        return False
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_ftp_server_manager():
    """Test FTP server manager functionality."""
    print("Testing FTPServerManager...")
    
    try:
        # Create server manager
        server_manager = FTPServerManager()
        
        # Test port availability check
        available = server_manager.is_port_available(2121)
        assert isinstance(available, bool), "Port availability check failed"
        print("  ✓ Port availability check: PASSED")
        
        # Test port range availability check
        range_available = server_manager.is_port_range_available(60000, 60010)
        assert isinstance(range_available, bool), "Port range availability check failed"
        print("  ✓ Port range availability check: PASSED")
        
        # Test running status (should be False initially)
        running = server_manager.is_running()
        assert running is False, "Server should not be running initially"
        print("  ✓ Initial running status check: PASSED")
        
        print("FTPServerManager tests: PASSED")
        return True
        
    except Exception as e:
        print(f"FTPServerManager tests: FAILED - {str(e)}")
        return False


def test_pyftp_application():
    """Test PyFTP application functionality."""
    print("Testing PyFTPApplication...")
    
    try:
        # Create application
        app = PyFTPApplication("test_config.ini")
        
        # Test initialization
        initialized = app.initialize()
        assert initialized is True, "Application initialization failed"
        print("  ✓ Application initialization: PASSED")
        
        # Test server running status (should be False initially)
        running = app.is_server_running()
        assert running is False, "Server should not be running initially"
        print("  ✓ Initial server running status check: PASSED")
        
        # Test connection count (should be 0 initially)
        conn_count = app.get_connection_count()
        assert conn_count == 0, "Connection count should be 0 initially"
        print("  ✓ Initial connection count check: PASSED")
        
        # Test port availability check
        available = app.is_port_available(2121)
        assert isinstance(available, bool), "Port availability check failed"
        print("  ✓ Port availability check: PASSED")
        
        print("PyFTPApplication tests: PASSED")
        return True
        
    except Exception as e:
        print(f"PyFTPApplication tests: FAILED - {str(e)}")
        return False


def main():
    """Run all tests."""
    print("Running PyFTP refactored code tests...\n")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_config_manager()
    print()
    
    all_passed &= test_ftp_server_manager()
    print()
    
    all_passed &= test_pyftp_application()
    print()
    
    if all_passed:
        print("All tests PASSED! ✅")
        return 0
    else:
        print("Some tests FAILED! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())