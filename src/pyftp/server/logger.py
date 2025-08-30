"""
Custom logging handler for displaying logs in the GUI.
"""

import logging
from PyQt5.QtCore import QObject, pyqtSignal


class QtLogHandler(QObject, logging.Handler):
    """Custom logging handler that emits Qt signals for GUI updates."""
    
    log_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', 
                                           datefmt='%Y-%m-%d %H:%M:%S'))
    
    def emit(self, record):
        """Emit a log record as a Qt signal."""
        msg = self.format(record)
        level = record.levelname
        self.log_signal.emit(msg, level)