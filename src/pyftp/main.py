#!/usr/bin/env python3
"""
Main entry point for the PyFTP server application.
"""

import sys
import os
import logging
from typing import NoReturn
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from pyftp.gui.window import FTPWindow


def main() -> NoReturn:
    """Main application entry point."""
    # 设置高DPI支持
    # 修复: 使用getattr安全地访问属性
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(getattr(Qt, 'AA_EnableHighDpiScaling'), True)
    # 修复类型检查错误: 通过 getattr 获取属性
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(getattr(Qt, 'AA_UseHighDpiPixmaps'), True)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用程序属性
    app.setApplicationName("PyFTP Server")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyFTP")
    
    # 不再直接配置根日志记录器，让GUI窗口来配置
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s %(levelname)s: %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S'
    # )
    
    window = FTPWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()