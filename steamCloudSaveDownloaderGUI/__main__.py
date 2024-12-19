import sys
from PySide6 import QtWidgets
from . import main_window
from .core import core
from . import data_provider
from .steamCloudSaveDownloader.steamCloudSaveDownloader import logger

def __main__():
    core.init()

    logger.setup_logger_post_config(core.s_log_file, data_provider.config['Log']['log_level'])
    logger.logger.info("scsd-gui started")

    app = QtWidgets.QApplication([])

    window = main_window.main_window()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())