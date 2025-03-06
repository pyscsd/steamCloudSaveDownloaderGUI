from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from .core import core

class status_bar(QW.QStatusBar):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('QStatusBar::item {border: None;}')

        self.label = QW.QLabel()
        self.addWidget(self.label)

        self.progress_bar = QW.QProgressBar()
        self.set_progress_bar_value(100)
        self.progress_bar.setTextVisible(False)
        self.addPermanentWidget(self.progress_bar)

        self.set_ready()

    @QtCore.Slot(int)
    def set_progress_bar_value(self, p_val: int):
        self.progress_bar.setValue(p_val)

    def set_authenticating(self):
        self.label.setText("Authenticating...")
        self.label.setStyleSheet("")

    def set_text(self, p_text: str):
        self.label.setText(p_text)
        self.label.setStyleSheet("")

    def download_in_progress(self) -> bool:
        return self.progress_bar.value() != 100
        # If progress bar is not 0 means download in progress

    def set_table_widget_tips(self):
        if self.download_in_progress():
            return
        self.label.setText("Double click to view files. Right click for options.")


    @QtCore.Slot()
    def set_ready(self):
        if self.download_in_progress():
            return

        if core.has_session():
            self.label.setText("Ready. Press 'Refresh' to populate list or 'Start' to start downloading.")
            self.label.setStyleSheet("")
        else:
            self.label.setText("No session. Please create session with Session > Login.")
            self.label.setStyleSheet("QLabel { color : red }")