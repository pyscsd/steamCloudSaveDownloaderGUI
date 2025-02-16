import os
import sys
from PySide6 import QtWidgets, QtGui
from . import main_window
from .core import core
from . import data_provider
from .steamCloudSaveDownloader.steamCloudSaveDownloader import logger
from .res import icon

def __main__():
    core.init()

    logger.setup_logger_post_config(core.s_log_file, data_provider.config['Log']['log_level'])
    logger.logger.info("scsd-gui started")

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/scsd_256.jpg")))

    window = main_window.main_window()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())