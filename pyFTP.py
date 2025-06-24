import sys
import os
import logging
import configparser
import warnings
import socket
from threading import Thread, Event
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QFileDialog, QCheckBox, QStatusBar, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QTextCursor, QIntValidator
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer, ThreadedFTPServer

# 抑制不必要的警告
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="write permissions assigned to anonymous user")

# 自定义日志处理器，用于UI显示
class QtLogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', 
                                           datefmt='%Y-%m-%d %H:%M:%S'))
    
    def emit(self, record):
        msg = self.format(record)
        level = record.levelname
        self.log_signal.emit(msg, level)

# FTP 服务器线程
class FTPServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self._stop_event = Event()
        self.daemon = True
    
    def run(self):
        while not self._stop_event.is_set():
            self.server.serve_forever(timeout=0.5, blocking=False)
    
    def stop(self):
        self._stop_event.set()
        self.server.close_all()

# 主应用窗口
class FTPWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = "ftpserver.ini"
        self.setup_ui()
        self.setup_logging()
        self.load_config()
        self.ftp_server_thread = None
        self.server_instance = None
        
    def setup_ui(self):
        self.setWindowTitle("PyFTP Server")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 配置组
        config_group = QGroupBox("服务器配置")
        config_layout = QVBoxLayout()
        
        # 端口设置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_edit = QLineEdit("2121")
        port_validator = QIntValidator(1, 65535, self.port_edit)
        self.port_edit.setValidator(port_validator)
        port_layout.addWidget(self.port_edit)
        port_layout.addStretch()
        config_layout.addLayout(port_layout)
        
        # 目录设置
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("根目录:"))
        self.dir_edit = QLineEdit(os.getcwd())
        dir_layout.addWidget(self.dir_edit)
        self.dir_button = QPushButton("浏览...")
        self.dir_button.clicked.connect(self.browse_dir)
        dir_layout.addWidget(self.dir_button)
        config_layout.addLayout(dir_layout)
        
        # 被动模式
        passive_layout = QHBoxLayout()
        self.passive_check = QCheckBox("启用被动模式")
        self.passive_check.setChecked(True)
        self.passive_check.stateChanged.connect(self.toggle_passive_fields)
        passive_layout.addWidget(self.passive_check)
        
        passive_sub_layout = QHBoxLayout()
        passive_sub_layout.addWidget(QLabel("被动端口范围:"))
        self.passive_start = QLineEdit("60000")
        passive_validator = QIntValidator(1024, 65535, self.passive_start)
        self.passive_start.setValidator(passive_validator)
        passive_sub_layout.addWidget(self.passive_start)
        passive_sub_layout.addWidget(QLabel("到"))
        self.passive_end = QLineEdit("61000")
        self.passive_end.setValidator(passive_validator)
        passive_sub_layout.addWidget(self.passive_end)
        passive_sub_layout.addStretch()
        
        passive_layout.addLayout(passive_sub_layout)
        config_layout.addLayout(passive_layout)
        
        # 编码设置
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("FTP编码:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItem("GBK (简体中文)")
        self.encoding_combo.addItem("UTF-8 (国际)")
        self.encoding_combo.setCurrentIndex(0)
        encoding_layout.addWidget(self.encoding_combo)
        encoding_layout.addStretch()
        
        # 线程模式
        threading_layout = QHBoxLayout()
        threading_layout.addWidget(QLabel("服务器模式:"))
        self.threading_combo = QComboBox()
        self.threading_combo.addItem("单线程模式")
        self.threading_combo.addItem("多线程模式")
        self.threading_combo.setCurrentIndex(1)
        threading_layout.addWidget(self.threading_combo)
        threading_layout.addStretch()
        
        config_layout.addLayout(encoding_layout)
        config_layout.addLayout(threading_layout)
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # 用户信息
        user_group = QGroupBox("用户配置")
        user_layout = QVBoxLayout()
        user_info = QHBoxLayout()
        user_info.addWidget(QLabel("当前配置: 匿名访问模式 (用户名: anonymous, 无密码)"))
        user_layout.addLayout(user_info)
        user_group.setLayout(user_layout)
        main_layout.addWidget(user_group)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("启动服务器")
        self.start_btn.clicked.connect(self.toggle_server)
        btn_layout.addWidget(self.start_btn)
        
        self.save_btn = QPushButton("保存配置")
        self.save_btn.clicked.connect(self.save_config)
        btn_layout.addWidget(self.save_btn)
        
        self.reload_btn = QPushButton("热重载配置")
        self.reload_btn.clicked.connect(self.reload_config)
        self.reload_btn.setEnabled(False)
        btn_layout.addWidget(self.reload_btn)
        
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(self.clear_log_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 日志显示
        log_group = QGroupBox("服务器日志")
        log_layout = QVBoxLayout()
        
        # 日志级别过滤
        log_filter_layout = QHBoxLayout()
        log_filter_layout.addWidget(QLabel("日志级别:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["全部", "信息", "警告", "错误"])
        self.log_level_combo.setCurrentIndex(0)
        self.log_level_combo.currentIndexChanged.connect(self.filter_logs)
        log_filter_layout.addWidget(self.log_level_combo)
        log_filter_layout.addStretch()
        log_layout.addLayout(log_filter_layout)
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                font-family: Consolas, Courier New, monospace;
                font-size: 10pt;
            }
        """)
        log_layout.addWidget(self.log_view)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("服务器已停止")
        
        # 初始化被动模式字段状态
        self.toggle_passive_fields()
    
    def toggle_passive_fields(self):
        enabled = self.passive_check.isChecked()
        self.passive_start.setEnabled(enabled)
        self.passive_end.setEnabled(enabled)
    
    def setup_logging(self):
        self.log_handler = QtLogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(self.log_handler)
        
        # 设置pyftpdlib的日志级别
        ftp_logger = logging.getLogger('pyftpdlib')
        ftp_logger.setLevel(logging.INFO)
        ftp_logger.addHandler(self.log_handler)
    
    def append_log(self, message, level):
        """添加日志到显示区域，根据级别着色"""
        if level == "WARNING":
            color = "#FFA500"
        elif level == "ERROR" or level == "CRITICAL":
            color = "#FF5555"
        elif level == "INFO":
            color = "#55AAFF"
        else:
            color = "#DCDCDC"
        
        # 保存当前滚动位置
        scrollbar = self.log_view.verticalScrollBar()
        at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # 添加带颜色的日志
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.setTextColor(QColor(color))
        self.log_view.insertPlainText(message + '\n')
        
        # 恢复滚动位置
        if at_bottom:
            scrollbar.setValue(scrollbar.maximum())
    
    def filter_logs(self):
        """根据选择的日志级别过滤日志"""
        level_index = self.log_level_combo.currentIndex()
        level_map = {0: None, 1: "INFO", 2: "WARNING", 3: "ERROR"}
        filter_level = level_map[level_index]
        
        # 获取所有日志内容
        full_text = self.log_view.toPlainText()
        lines = full_text.split('\n')
        
        # 清空并重新添加过滤后的日志
        self.log_view.clear()
        
        for line in lines:
            if not line:
                continue
                
            if filter_level is None or f" {filter_level}:" in line:
                if " WARNING:" in line:
                    color = "#FFA500"
                elif " ERROR:" in line or " CRITICAL:" in line:
                    color = "#FF5555"
                elif " INFO:" in line:
                    color = "#55AAFF"
                else:
                    color = "#DCDCDC"
                
                self.log_view.setTextColor(QColor(color))
                self.log_view.append(line)
        
        # 滚动到底部
        self.log_view.moveCursor(QTextCursor.End)
    
    def clear_log(self):
        """清空日志显示"""
        self.log_view.clear()
        logging.info("日志已清空")
    
    def browse_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择FTP根目录")
        if directory:
            self.dir_edit.setText(directory)
    
    def load_config(self):
        config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file, encoding='utf-8')
                
                if config.has_section('server'):
                    self.port_edit.setText(config.get('server', 'port', fallback='2121'))
                    self.dir_edit.setText(config.get('server', 'directory', fallback=os.getcwd()))
                    
                    passive_enabled = config.getboolean('server', 'passive', fallback=True)
                    self.passive_check.setChecked(passive_enabled)
                    
                    self.passive_start.setText(config.get('server', 'passive_start', fallback='60000'))
                    self.passive_end.setText(config.get('server', 'passive_end', fallback='61000'))
                    
                    encoding_idx = int(config.get('server', 'encoding', fallback='0'))
                    self.encoding_combo.setCurrentIndex(encoding_idx)
                    
                    threading_idx = int(config.get('server', 'threading', fallback='1'))
                    self.threading_combo.setCurrentIndex(threading_idx)
                    
                    logging.info("配置文件已加载")
            except Exception as e:
                logging.error(f"加载配置失败: {str(e)}，使用默认配置")
        else:
            logging.warning("配置文件不存在，使用默认配置")
            # 创建默认配置
            self.save_config()
    
    def save_config(self):
        config = configparser.ConfigParser()
        
        config.add_section('server')
        try:
            config.set('server', 'port', self.port_edit.text())
            config.set('server', 'directory', self.dir_edit.text())
            config.set('server', 'passive', str(self.passive_check.isChecked()))
            config.set('server', 'passive_start', self.passive_start.text())
            config.set('server', 'passive_end', self.passive_end.text())
            config.set('server', 'encoding', str(self.encoding_combo.currentIndex()))
            config.set('server', 'threading', str(self.threading_combo.currentIndex()))
            
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            logging.info("配置保存成功")
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
    
    def reload_config(self):
        if self.ftp_server_thread and self.ftp_server_thread.is_alive():
            logging.info("正在重新加载配置...")
            self.stop_server()
            self.start_server()
    
    def get_server_config(self):
        return {
            'port': int(self.port_edit.text() or 2121),
            'directory': self.dir_edit.text() or os.getcwd(),
            'passive': self.passive_check.isChecked(),
            'passive_start': int(self.passive_start.text() or 60000),
            'passive_end': int(self.passive_end.text() or 61000),
            'encoding': 'gbk' if self.encoding_combo.currentIndex() == 0 else 'utf-8',
            'threading': self.threading_combo.currentIndex() == 1
        }
    
    def start_server(self):
        config = self.get_server_config()
        
        if not self.is_port_available(config['port']):
            logging.error(f"端口 {config['port']} 已被占用，请选择其他端口")
            QMessageBox.critical(self, "端口冲突", f"端口 {config['port']} 已被占用，请选择其他端口")
            return False
        
        if config['passive']:
            if config['passive_start'] >= config['passive_end']:
                logging.error("被动端口范围无效: 起始端口必须小于结束端口")
                QMessageBox.critical(self, "配置错误", "被动端口范围无效: 起始端口必须小于结束端口")
                return False
            
            if not self.is_port_range_available(config['passive_start'], config['passive_end']):
                logging.error("被动端口范围已被占用或不可用")
                QMessageBox.critical(self, "端口冲突", "被动端口范围已被占用或不可用")
                return False
        
        if not os.path.isdir(config['directory']):
            logging.error(f"目录不存在: {config['directory']}")
            QMessageBox.critical(self, "目录错误", f"目录不存在: {config['directory']}")
            return False
        
        try:
            authorizer = DummyAuthorizer()
            authorizer.add_anonymous(config['directory'], perm="elradfmw")
            
            warnings.filterwarnings("ignore", category=RuntimeWarning, 
                                   message="write permissions assigned to anonymous user")
            
            class CustomHandler(FTPHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if config['passive']:
                        self.passive_ports = range(
                            config['passive_start'], 
                            config['passive_end'] + 1
                        )
                
                def on_connect(self):
                    logging.info(f"新连接来自: {self.remote_ip}:{self.remote_port}")
                
                def on_login(self, username):
                    logging.info(f"用户登录: {username}@{self.remote_ip}")
                
                def on_disconnect(self):
                    logging.info(f"连接关闭: {self.remote_ip}:{self.remote_port}")
            
            handler = CustomHandler
            handler.authorizer = authorizer
            handler.encoding = config['encoding']
            handler.log_prefix = "%(remote_ip)s:%(remote_port)s"  # 修正日志前缀设置
            
            server_class = ThreadedFTPServer if config['threading'] else FTPServer
            self.server_instance = server_class(("0.0.0.0", config['port']), handler)
            self.server_instance.max_cons = 256
            self.server_instance.max_cons_per_ip = 5
            
            self.ftp_server_thread = FTPServerThread(self.server_instance)
            self.ftp_server_thread.start()
            
            self.start_btn.setText("停止服务器")
            self.status_bar.showMessage(
                f"服务器运行中: 端口 {config['port']}, "
                f"目录 {config['directory']}, "
                f"编码 {config['encoding'].upper()}, "
                f"{'多线程' if config['threading'] else '单线程'}模式"
            )
            self.reload_btn.setEnabled(True)
            
            if config['passive']:
                logging.info(f"被动模式已启用 - 端口范围: {config['passive_start']}-{config['passive_end']}")
            
            logging.info(f"FTP服务器已启动 ({'多线程' if config['threading'] else '单线程'}模式)")
            return True
            
        except Exception as e:
            logging.error(f"启动服务器失败: {str(e)}")
            QMessageBox.critical(self, "服务器错误", f"启动服务器失败: {str(e)}")
            return False
    
    def is_port_available(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", port))
            s.close()
            return True
        except:
            return False
    
    def is_port_range_available(self, start, end):
        for port in range(start, end + 1):
            if not self.is_port_available(port):
                return False
        return True
    
    def stop_server(self):
        if self.ftp_server_thread and self.ftp_server_thread.is_alive():
            try:
                self.ftp_server_thread.stop()
                self.ftp_server_thread.join(timeout=2.0)
                
                if self.ftp_server_thread.is_alive():
                    logging.warning("服务器线程仍在运行，强制终止")
                    self.server_instance.close_all()
                
                self.ftp_server_thread = None
                self.server_instance = None
                self.start_btn.setText("启动服务器")
                self.status_bar.showMessage("服务器已停止")
                self.reload_btn.setEnabled(False)
                logging.info("FTP服务器已停止")
            except Exception as e:
                logging.error(f"停止服务器失败: {str(e)}")
                QMessageBox.critical(self, "服务器错误", f"停止服务器失败: {str(e)}")
    
    def toggle_server(self):
        if self.ftp_server_thread and self.ftp_server_thread.is_alive():
            self.stop_server()
        else:
            self.start_server()
    
    def closeEvent(self, event):
        if self.ftp_server_thread and self.ftp_server_thread.is_alive():
            self.stop_server()
            QTimer.singleShot(500, self.close)
            event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = FTPWindow()
    window.show()
    sys.exit(app.exec_())
