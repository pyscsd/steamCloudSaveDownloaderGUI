import sys
import traceback
from PySide6 import QtWidgets, QtGui
from . import main_window
from .core import core
from . import data_provider
from .steamCloudSaveDownloader.steamCloudSaveDownloader import logger
from .res import icon

def main():
    core.init()

    if core.s_initial_config_reload_required:
        data_provider.reload_config()

    logger.setup_logger_post_config(core.s_log_file, data_provider.config['Log']['log_level'])
    logger.logger.info("scsd-gui started")

    core.set_start_on_startup(data_provider.config['GUI']['auto_start'])

    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(":/scsd_256.jpg")))

    window = main_window.main_window()
    window.resize(800, 600)

    if len(sys.argv) == 2 and sys.argv[1] == '--minimize':
        window.hide()
    else:
        window.show()

    sys.exit(app.exec())

def __main__():
    try:
        main()
    except Exception as e:
        ec = traceback.format_exc()
        print(ec)
        logger.error(ec)