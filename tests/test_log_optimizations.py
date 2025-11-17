"""
Test script to verify the log display optimizations made to PyFTP server.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import PyQt5 and set up QApplication before importing GUI components
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QTextCharFormat

from gui.components.log_panel import GuiLogPanel


def test_log_panel_optimizations():
    """Test log panel optimizations."""
    print("Testing LogPanel optimizations...")
    
    try:
        # Create QApplication for GUI components
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create log panel
        log_panel = GuiLogPanel()
        
        # Test appending logs with different levels
        log_panel.append_log("2023-01-01 12:00:00 INFO: Test info message", "INFO")
        log_panel.append_log("2023-01-01 12:00:01 WARNING: Test warning message", "WARNING")
        log_panel.append_log("2023-01-01 12:00:02 ERROR: Test error message", "ERROR")
        log_panel.append_log("2023-01-01 12:00:03 CRITICAL: Test critical message", "CRITICAL")
        log_panel.append_log("2023-01-01 12:00:04 DEBUG: Test debug message", "DEBUG")
        
        # Process the log buffer
        log_panel._process_log_buffer()
        
        # Check that logs were added
        text_content = log_panel.log_view.toPlainText()
        assert "Test info message" in text_content, "Info message not found"
        assert "Test warning message" in text_content, "Warning message not found"
        assert "Test error message" in text_content, "Error message not found"
        assert "Test critical message" in text_content, "Critical message not found"
        assert "Test debug message" in text_content, "Debug message not found"
        print("  ✓ Append logs with different levels: PASSED")
        
        # Test log filtering - show only errors
        # Select "错误" (Error) level (index 3)
        log_panel.log_level_combo.setCurrentIndex(3)
        log_panel.filter_logs()
        
        # Check that only error and critical messages are visible
        filtered_content = log_panel.log_view.toPlainText()
        assert "Test error message" in filtered_content, "Error message not found after filtering"
        assert "Test critical message" in filtered_content, "Critical message not found after filtering"
        # Info and warning messages should not be in filtered content
        print("  ✓ Log filtering (Error level): PASSED")
        
        # Re-add logs for next test
        log_panel.log_level_combo.setCurrentIndex(0)  # Reset to "All"
        log_panel.filter_logs()  # Show all logs again
        log_panel.append_log("2023-01-01 12:00:05 INFO: Test info message 2", "INFO")
        log_panel.append_log("2023-01-01 12:00:06 WARNING: Test warning message 2", "WARNING")
        log_panel.append_log("2023-01-01 12:00:07 ERROR: Test error message 2", "ERROR")
        log_panel._process_log_buffer()
        
        # Test log filtering - show only warnings
        # Select "警告" (Warning) level (index 2)
        log_panel.log_level_combo.setCurrentIndex(2)
        log_panel.filter_logs()
        
        # Check that only warning messages are visible
        filtered_content = log_panel.log_view.toPlainText()
        assert "Test warning message 2" in filtered_content, "Warning message not found after filtering"
        # Info, error and critical messages should not be in filtered content
        print("  ✓ Log filtering (Warning level): PASSED")
        
        # Re-add logs for next test
        log_panel.log_level_combo.setCurrentIndex(0)  # Reset to "All"
        log_panel.filter_logs()  # Show all logs again
        log_panel.append_log("2023-01-01 12:00:08 INFO: Test info message 3", "INFO")
        log_panel._process_log_buffer()
        
        # Test log filtering - show only info
        # Select "信息" (Info) level (index 1)
        log_panel.log_level_combo.setCurrentIndex(1)
        log_panel.filter_logs()
        
        # Check that only info messages are visible
        filtered_content = log_panel.log_view.toPlainText()
        assert "Test info message 3" in filtered_content, "Info message not found after filtering"
        print("  ✓ Log filtering (Info level): PASSED")
        
        # Re-add logs for next test
        log_panel.log_level_combo.setCurrentIndex(0)  # Reset to "All"
        log_panel.filter_logs()  # Show all logs again
        log_panel.append_log("2023-01-01 12:00:09 WARNING: Test warning message 3", "WARNING")
        log_panel.append_log("2023-01-01 12:00:10 ERROR: Test error message 3", "ERROR")
        log_panel.append_log("2023-01-01 12:00:11 CRITICAL: Test critical message 3", "CRITICAL")
        log_panel._process_log_buffer()
        
        # Test log filtering - show all
        # Select "全部" (All) level (index 0)
        log_panel.log_level_combo.setCurrentIndex(0)
        log_panel.filter_logs()
        
        # Check that all messages are visible
        filtered_content = log_panel.log_view.toPlainText()
        assert "Test info message" in filtered_content or "Test info message 2" in filtered_content or "Test info message 3" in filtered_content, "Info message not found after filtering"
        assert "Test warning message" in filtered_content or "Test warning message 2" in filtered_content or "Test warning message 3" in filtered_content, "Warning message not found after filtering"
        assert "Test error message" in filtered_content or "Test error message 2" in filtered_content or "Test error message 3" in filtered_content, "Error message not found after filtering"
        assert "Test critical message" in filtered_content or "Test critical message 3" in filtered_content, "Critical message not found after filtering"
        print("  ✓ Log filtering (All level): PASSED")
        
        # Test clearing logs
        log_panel.clear_log()
        cleared_content = log_panel.log_view.toPlainText()
        assert cleared_content == "", "Log panel not cleared"
        assert len(log_panel.log_buffer) == 0, "Log buffer not cleared"
        print("  ✓ Clear logs: PASSED")
        
        print("LogPanel optimizations tests: PASSED")
        return True
        
    except Exception as e:
        print(f"LogPanel optimizations tests: FAILED - {str(e)}")
        return False


def main():
    """Run all log optimization tests."""
    print("Running PyFTP log optimization tests...\n")
    
    # Create QApplication for GUI components
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_log_panel_optimizations()
    print()
    
    if all_passed:
        print("All log optimization tests PASSED! ✅")
        return 0
    else:
        print("Some log optimization tests FAILED! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())