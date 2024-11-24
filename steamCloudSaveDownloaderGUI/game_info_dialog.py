from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from . import data_provider

class game_info_dialog(QW.QDialog):
    def __init__(self, app_id: int, game_name: str):
        super().__init__()

        self.setWindowTitle(f"{game_name} Saves")

        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def create_widgets(self):
        pass
    def layout_widgets(self):
        pass
    def connect_signals(self):
        pass