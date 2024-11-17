from PySide6 import QtWidgets
from . import menu
from . import status_bar

class main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.status_bar = status_bar.status_bar()
        self.setStatusBar(self.status_bar)

        self.menu_bar = menu.menu_bar(self, self.status_bar)
        self.setMenuBar(self.menu_bar)

        self.setWindowTitle("scsd-gui")