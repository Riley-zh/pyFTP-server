#!/usr/bin/env python3
"""
Main entry point for the PyFTP server application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from pyftp.gui.window import FTPWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = FTPWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()