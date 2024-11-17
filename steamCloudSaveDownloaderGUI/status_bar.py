from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from .core import core

class status_bar(QW.QStatusBar):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('QStatusBar::item {border: None;}')

        self.label = QW.QLabel()
        self.addWidget(self.label)

        self.set_ready()


    # TODO: Pass to Menu
    @QtCore.Slot()
    def set_ready(self):
        if core.has_session():
            self.label.setText("Ready. Press Start to start downloading.")
            self.label.setStyleSheet("")
        else:
            self.label.setText("No session. Please create session with Session > Login.")
            self.label.setStyleSheet("QLabel { color : red }")