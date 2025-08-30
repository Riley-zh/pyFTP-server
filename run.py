#!/usr/bin/env python3
"""
Simple run script to test the refactored PyFTP server application.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pyftp.main import main

if __name__ == "__main__":
    main()