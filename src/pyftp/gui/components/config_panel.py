"""
Configuration panel for the FTP server settings.
"""

import os
from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox
)
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QIntValidator

from pyftp.core.constants import (
    DEFAULT_PORT, DEFAULT_DIRECTORY, DEFAULT_PASSIVE_MODE,
    DEFAULT_PASSIVE_START, DEFAULT_PASSIVE_END, 
    ENCODING_OPTIONS, THREADING_OPTIONS
)
from pyftp.utils.helpers import validate_directory


class ConfigPanel(QGroupBox):
    """Configuration panel for FTP server settings."""
    
    # Signals
    directory_browse_requested = pyqtSignal()
    config_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__("服务器配置")
        self.setup_ui()
        self._setup_validators()
        self._connect_signals()
    
    def setup_ui(self):
        """Setup the configuration UI."""
        config_layout = QVBoxLayout()
        
        # 端口设置
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("端口:"))
        self.port_edit = QLineEdit(str(DEFAULT_PORT))
        port_layout.addWidget(self.port_edit)
        port_layout.addStretch()
        config_layout.addLayout(port_layout)
        
        # 目录设置
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("根目录:"))
        self.dir_edit = QLineEdit(os.getcwd())
        dir_layout.addWidget(self.dir_edit)
        self.dir_button = QPushButton("浏览...")
        dir_layout.addWidget(self.dir_button)
        config_layout.addLayout(dir_layout)
        
        # 被动模式
        passive_layout = QHBoxLayout()
        self.passive_check = QCheckBox("启用被动模式")
        self.passive_check.setChecked(DEFAULT_PASSIVE_MODE)
        self.passive_check.stateChanged.connect(self.toggle_passive_fields)
        passive_layout.addWidget(self.passive_check)
        
        passive_sub_layout = QHBoxLayout()
        passive_sub_layout.addWidget(QLabel("被动端口范围:"))
        self.passive_start = QLineEdit(str(DEFAULT_PASSIVE_START))
        passive_sub_layout.addWidget(self.passive_start)
        passive_sub_layout.addWidget(QLabel("到"))
        self.passive_end = QLineEdit(str(DEFAULT_PASSIVE_END))
        passive_sub_layout.addWidget(self.passive_end)
        passive_sub_layout.addStretch()
        
        passive_layout.addLayout(passive_sub_layout)
        config_layout.addLayout(passive_layout)
        
        # 编码设置
        encoding_layout = QHBoxLayout()
        encoding_layout.addWidget(QLabel("FTP编码:"))
        self.encoding_combo = QComboBox()
        for _, label, _ in ENCODING_OPTIONS:
            self.encoding_combo.addItem(label)
        self.encoding_combo.setCurrentIndex(0)
        encoding_layout.addWidget(self.encoding_combo)
        encoding_layout.addStretch()
        
        # 线程模式
        threading_layout = QHBoxLayout()
        threading_layout.addWidget(QLabel("服务器模式:"))
        self.threading_combo = QComboBox()
        for _, label in THREADING_OPTIONS:
            self.threading_combo.addItem(label)
        self.threading_combo.setCurrentIndex(1)
        threading_layout.addWidget(self.threading_combo)
        threading_layout.addStretch()
        
        config_layout.addLayout(encoding_layout)
        config_layout.addLayout(threading_layout)
        self.setLayout(config_layout)
    
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        self.dir_button.clicked.connect(self.directory_browse_requested)
        
        # Connect all config change signals
        self.port_edit.textChanged.connect(self._on_config_changed)
        self.dir_edit.textChanged.connect(self._on_config_changed)
        self.passive_check.stateChanged.connect(self._on_config_changed)
        self.passive_start.textChanged.connect(self._on_config_changed)
        self.passive_end.textChanged.connect(self._on_config_changed)
        self.encoding_combo.currentIndexChanged.connect(self._on_config_changed)
        self.threading_combo.currentIndexChanged.connect(self._on_config_changed)
    
    def _on_config_changed(self):
        """Handle configuration changes."""
        self.config_changed.emit()
    
    def _setup_validators(self):
        """Setup input validators with delayed validation."""
        # 使用定时器延迟验证，避免用户输入时频繁验证
        self.port_validator = QIntValidator(1, 65535)
        self.passive_start_validator = QIntValidator(1024, 65535)
        self.passive_end_validator = QIntValidator(1024, 65535)
        
        # 定时器用于延迟验证
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self._perform_validation)
        
        # 连接输入变化信号
        self.port_edit.textChanged.connect(lambda: self._schedule_validation('port'))
        self.passive_start.textChanged.connect(lambda: self._schedule_validation('passive_start'))
        self.passive_end.textChanged.connect(lambda: self._schedule_validation('passive_end'))
    
    def _schedule_validation(self, field):
        """Schedule validation with a delay."""
        # 重新启动定时器
        self.validation_timer.stop()
        self.validation_timer.start(500)  # 500ms延迟
    
    def _perform_validation(self):
        """Perform validation on all fields."""
        # 验证端口
        port_text = self.port_edit.text()
        if port_text:
            try:
                port = int(port_text)
                if not (1 <= port <= 65535):
                    self.port_edit.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
                else:
                    self.port_edit.setStyleSheet("")
            except ValueError:
                self.port_edit.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
        else:
            self.port_edit.setStyleSheet("")
        
        # 验证被动端口范围
        start_text = self.passive_start.text()
        end_text = self.passive_end.text()
        
        if start_text and end_text:
            try:
                start = int(start_text)
                end = int(end_text)
                if not (1024 <= start <= 65535) or not (1024 <= end <= 65535) or start >= end:
                    self.passive_start.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
                    self.passive_end.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
                else:
                    self.passive_start.setStyleSheet("")
                    self.passive_end.setStyleSheet("")
            except ValueError:
                self.passive_start.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
                self.passive_end.setStyleSheet("QLineEdit { background-color: #FFCCCC; }")
        else:
            self.passive_start.setStyleSheet("")
            self.passive_end.setStyleSheet("")
    
    def toggle_passive_fields(self):
        """Enable/disable passive mode fields based on checkbox state."""
        enabled = self.passive_check.isChecked()
        self.passive_start.setEnabled(enabled)
        self.passive_end.setEnabled(enabled)
    
    def get_config(self):
        """Get current configuration as a dictionary."""
        encoding_value = ENCODING_OPTIONS[self.encoding_combo.currentIndex()][2]
        return {
            'port': int(self.port_edit.text() or DEFAULT_PORT),
            'directory': self.dir_edit.text() or os.getcwd(),
            'passive': self.passive_check.isChecked(),
            'passive_start': int(self.passive_start.text() or DEFAULT_PASSIVE_START),
            'passive_end': int(self.passive_end.text() or DEFAULT_PASSIVE_END),
            'encoding': encoding_value,
            'encoding_idx': self.encoding_combo.currentIndex(),
            'threading': self.threading_combo.currentIndex() == 1,
            'threading_idx': self.threading_combo.currentIndex()
        }
    
    def load_config(self, config_data):
        """Load configuration from a dictionary."""
        self.port_edit.setText(str(config_data.get('port', DEFAULT_PORT)))
        self.dir_edit.setText(config_data.get('directory', os.getcwd()))
        
        passive_enabled = config_data.get('passive', DEFAULT_PASSIVE_MODE)
        self.passive_check.setChecked(passive_enabled)
        
        self.passive_start.setText(str(config_data.get('passive_start', DEFAULT_PASSIVE_START)))
        self.passive_end.setText(str(config_data.get('passive_end', DEFAULT_PASSIVE_END)))
        
        encoding_idx = config_data.get('encoding_idx', 0)
        self.encoding_combo.setCurrentIndex(encoding_idx)
        
        threading_idx = config_data.get('threading_idx', 1)
        self.threading_combo.setCurrentIndex(threading_idx)
    
    def validate_config(self):
        """Validate current configuration and return any errors."""
        errors = []
        config = self.get_config()
        
        # Validate port
        if not (1 <= config['port'] <= 65535):
            errors.append(f"端口 {config['port']} 无效，必须在 1-65535 范围内")
        
        # Validate directory
        if not validate_directory(config['directory']):
            errors.append(f"目录不存在或无法访问: {config['directory']}")
        
        # Validate passive mode settings
        if config['passive']:
            if not (1024 <= config['passive_start'] <= 65535):
                errors.append(f"被动起始端口 {config['passive_start']} 无效")
            if not (1024 <= config['passive_end'] <= 65535):
                errors.append(f"被动结束端口 {config['passive_end']} 无效")
            if config['passive_start'] >= config['passive_end']:
                errors.append("被动端口范围无效: 起始端口必须小于结束端口")
        
        return errors