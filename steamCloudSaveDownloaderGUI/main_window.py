from PySide6 import QtWidgets
from . import menu

class main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMenuBar(menu.menu_bar());
        self.setWindowTitle("scsd-gui")