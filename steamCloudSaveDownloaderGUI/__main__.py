import sys
from PySide6 import QtWidgets
from . import main_window

def __main__():
    app = QtWidgets.QApplication([])

    window = main_window.main_window()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())