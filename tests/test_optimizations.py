"""
Test script to verify the optimizations made to PyFTP server.
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
from pyftp.server.port_cache import get_port_cache


def test_config_manager_optimizations():
    """Test configuration manager optimizations."""
    print("Testing ConfigManager optimizations...")
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    config_file = os.path.join(test_dir, "test_config.ini")
    
    try:
        # Create config manager
        config_manager = ConfigManager(config_file)
        
        # Test saving config with encoding and threading options
        test_config = {
            'port': 2121,
            'directory': test_dir,
            'passive': True,
            'passive_start': 60000,
            'passive_end': 61000,
            'encoding_idx': 1,  # UTF-8
            'threading_idx': 0  # Single-threaded
        }
        
        success = config_manager.save_config(test_config)
        assert success, "Failed to save configuration"
        print("  ✓ Save configuration with encoding/threading options: PASSED")
        
        # Check the content of the saved config file
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  Config file content:\n{content}")
        
        # Test loading config
        loaded_config = config_manager.load_config()
        assert loaded_config is not None, "Failed to load configuration"
        assert loaded_config['port'] == 2121, "Port mismatch"
        assert loaded_config['directory'] == test_dir, "Directory mismatch"
        assert loaded_config['encoding_idx'] == 1, f"Encoding index mismatch: expected 1, got {loaded_config['encoding_idx']}"
        assert loaded_config['threading_idx'] == 0, f"Threading index mismatch: expected 0, got {loaded_config['threading_idx']}"
        print("  ✓ Load configuration with encoding/threading options: PASSED")
        
        print("ConfigManager optimizations tests: PASSED")
        return True
        
    except Exception as e:
        print(f"ConfigManager optimizations tests: FAILED - {str(e)}")
        return False
    finally:
        # Clean up
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_port_cache_optimizations():
    """Test port cache optimizations."""
    print("Testing PortCache optimizations...")
    
    try:
        # Get port cache instance
        port_cache = get_port_cache()
        
        # Test port availability check
        available = port_cache.is_port_available(2121)
        assert isinstance(available, bool), "Port availability check failed"
        print("  ✓ Port availability check: PASSED")
        
        # Test port range availability check
        range_available = port_cache.is_port_range_available(60000, 60010)
        assert isinstance(range_available, bool), "Port range availability check failed"
        print("  ✓ Port range availability check: PASSED")
        
        # Test cache cleanup
        port_cache.cleanup_expired()
        print("  ✓ Cache cleanup: PASSED")
        
        print("PortCache optimizations tests: PASSED")
        return True
        
    except Exception as e:
        print(f"PortCache optimizations tests: FAILED - {str(e)}")
        return False


def test_ftp_server_manager_optimizations():
    """Test FTP server manager optimizations."""
    print("Testing FTPServerManager optimizations...")
    
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
        
        print("FTPServerManager optimizations tests: PASSED")
        return True
        
    except Exception as e:
        print(f"FTPServerManager optimizations tests: FAILED - {str(e)}")
        return False


def main():
    """Run all optimization tests."""
    print("Running PyFTP optimization tests...\n")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_config_manager_optimizations()
    print()
    
    all_passed &= test_port_cache_optimizations()
    print()
    
    all_passed &= test_ftp_server_manager_optimizations()
    print()
    
    if all_passed:
        print("All optimization tests PASSED! ✅")
        return 0
    else:
        print("Some optimization tests FAILED! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())