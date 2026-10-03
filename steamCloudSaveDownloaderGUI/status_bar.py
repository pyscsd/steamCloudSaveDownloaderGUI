from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from .core import core

class status_bar(QW.QStatusBar):
    def __init__(self):
        super().__init__()

        self.setStyleSheet('QStatusBar::item {border: None;}')

        self.label = QW.QLabel()
        # Stretch factor 1 → label eats all free horizontal space so the
        # progress bar stays pinned on the right instead of jumping when
        # the label text length changes.
        self.addWidget(self.label, 1)

        self._in_progress = False
        self.progress_bar = QW.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)

        self.set_ready()

    @QtCore.Slot(int)
    def set_progress_bar_value(self, p_val: int):
        self.progress_bar.setValue(p_val)
        # 100 = just finished; anything else means a job is running.
        was_in_progress = self._in_progress
        self._in_progress = p_val != 100
        self.progress_bar.setVisible(self._in_progress)
        # Workers may clear their text before reporting 100, while set_ready()
        # still sees a job running and does nothing; reset the label here.
        if was_in_progress and not self._in_progress:
            self.set_ready()

    def set_authenticating(self):
        self.label.setText(self.tr("Authenticating..."))
        self.label.setStyleSheet("")

    def set_text(self, p_text: str):
        self.label.setText(p_text)
        self.label.setStyleSheet("")

    def download_in_progress(self) -> bool:
        # Not isVisible(): that is False whenever the window is hidden to tray.
        return self._in_progress

    def set_table_widget_tips(self):
        if self.download_in_progress():
            return
        self.label.setText(self.tr("Double click to view files. Right click for options."))


    @QtCore.Slot()
    def set_ready(self):
        if self.download_in_progress():
            return

        if core.has_session():
            self.label.setText(self.tr("Ready. Press 'Refresh' to populate list or 'Start' to start downloading."))
            self.label.setStyleSheet("")
        else:
            self.label.setText(self.tr("No session. Please create session with Session > Login."))
            self.label.setStyleSheet("QLabel { color : red }")