#!/usr/bin/env python3
"""
Simple run script to test the refactored PyFTP server application.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 设置环境变量以优化性能
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

from pyftp.main import main

if __name__ == "__main__":
    main()