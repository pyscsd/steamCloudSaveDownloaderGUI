from PySide6 import QtCore, QtGui, QtWidgets
from .core import core
from . import save_downloader
from . import thread_controller
from .dialogs import login_dialog, options_dialog
from .status_bar import status_bar

from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger
import os

class login_action(QtGui.QAction):
    login_success_signal = QtCore.Signal()

    def __init__(self, p_status_bar:status_bar):
        super().__init__("Login")
        self.status_bar = p_status_bar
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.dialog = login_dialog()
        result:QtWidgets.QDialog.DialogCode = self.dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.login_success_signal.emit()
        self.status_bar.set_ready()

class logout_action(QtGui.QAction):
    logout_signal = QtCore.Signal()
    def __init__(self, p_status_bar:status_bar):
        super().__init__("Logout")
        self.status_bar = p_status_bar

        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        if (core.has_session()):
            os.remove(core.s_session_file)
            self.logout_signal.emit()
        self.status_bar.set_ready()

class session_menu(QtWidgets.QMenu):
    login_success_signal = QtCore.Signal()
    logout_signal = QtCore.Signal()

    def __init__(self, p_status_bar:status_bar):
        super().__init__("Session")
        self.status_bar = p_status_bar

        self.login_action = login_action(p_status_bar)
        self.logout_action = logout_action(p_status_bar)
        self.addAction(self.login_action)

        self.addAction(self.logout_action)
        self.aboutToShow.connect(self.on_menu_to_show)
        self.login_action.login_success_signal.connect(self.login_success)
        self.logout_action.logout_signal.connect(self.logout_complete)

    @QtCore.Slot()
    def on_menu_to_show(self):
        self.logout_action.setEnabled(core.has_session())

    @QtCore.Slot()
    def login_success(self):
        self.login_success_signal.emit()

    @QtCore.Slot()
    def logout_complete(self):
        self.logout_signal.emit()

class options_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Options")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.dialog = options_dialog()
        self.dialog.exec()

class refresh_action(QtGui.QAction):
    data_updated_signal = QtCore.Signal()

    def __init__(self):
        super().__init__("Refresh")
        self.triggered.connect(self.execute)

        has_session:bool = core.has_session()
        self.setEnabled(has_session)

    @QtCore.Slot()
    def execute(self, p_action):
        logger.info("Refresh")
        self.data_updated_signal.emit()

    def set_enable(self, p_b: bool):
        self.setEnabled(p_b)

class download_all_action(QtGui.QAction):
    row_updated_signal = QtCore.Signal(int)

    def __init__(self, p_status_bar:status_bar):
        super().__init__()
        self.setText("Download All")
        self.status_bar = p_status_bar

        has_session:bool = core.has_session()
        self.setEnabled(has_session)

        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def app_id_updated(self, p_int: int):
        self.row_updated_signal.emit(p_int)

    @QtCore.Slot()
    def download_complete(self):
        self.status_bar.set_ready()

    @QtCore.Slot()
    def execute(self, p_action):
        logger.debug("Download All Executed")
        self.downloader = save_downloader.save_downloader(save_downloader.mode_e.download_all, self.status_bar)
        self.downloader.job_finished.connect(self.download_complete)
        self.downloader.job_notified.connect(self.app_id_updated)
        self.downloader.one_shot_download()

    @QtCore.Slot()
    def on_main_window_closed(self):
        if hasattr(self, "downloader_controller"):
            self.downloader_controller.stop()

class download_action(QtGui.QAction):
    row_updated_signal = QtCore.Signal(int)
    def __init__(self, p_status_bar:status_bar):
        super().__init__()
        self.setText("Download")

        self.status_bar = p_status_bar

        has_session:bool = core.has_session()
        self.setEnabled(has_session)

        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def download_complete(self):
        self.status_bar.set_ready()

    @QtCore.Slot()
    def app_id_updated(self, p_int: int):
        self.row_updated_signal.emit(p_int)

    @QtCore.Slot()
    def execute(self, p_action):
        logger.debug("Download Executed")
        self.downloader = save_downloader.save_downloader(save_downloader.mode_e.download_local_outdated, self.status_bar)
        self.downloader.job_finished.connect(self.download_complete)
        self.downloader.job_notified.connect(self.app_id_updated)
        self.downloader.one_shot_download()

    @QtCore.Slot()
    def on_main_window_closed(self):
        if hasattr(self, "downloader_controller"):
            self.downloader_controller.stop()

class start_stop_action(QtGui.QAction):
    data_updated_signal = QtCore.Signal(list)

    def __init__(self):
        super().__init__()
        self.start_state = True
        self.triggered.connect(self.execute)
        self.set_text()
        self.set_can_enable()

    def set_can_enable(self):
        has_session:bool = core.has_session()
        self.setEnabled(has_session)

        if not has_session:
            self.start_state = True
        self.set_text()

    def set_text(self):
        if self.start_state:
            self.setText("Start (TODO)")
        else:
            self.setText("Stop (TODO)")

    @QtCore.Slot()
    def execute(self, p_action):
        if self.start_state:
            self.start_state = False
            self.set_text()

            self.data_updated_signal.emit(list())
        else:
            self.start_state = True
            self.set_text()

class menu_bar(QtWidgets.QMenuBar):
    def __init__(self, p_parent:QtWidgets, p_status_bar:status_bar):
        super().__init__()
        self.parent = p_parent
        self.status_bar = p_status_bar

        self.session_menu = session_menu(p_status_bar)
        self.options_action = options_action()
        self.start_stop_action = start_stop_action()
        self.download_action = download_action(p_status_bar)
        self.download_all_action = download_all_action(p_status_bar)
        self.refresh_action = refresh_action()
        self.addMenu(self.session_menu)
        self.addAction(self.options_action)
        self.addAction(self.refresh_action)
        self.addAction(self.start_stop_action)
        self.addAction(self.download_action)
        self.addAction(self.download_all_action)

        self.connect_signals()

    def connect_signals(self):
        self.session_menu.login_success_signal.connect(self.session_change)
        self.session_menu.logout_signal.connect(self.session_change)

    @QtCore.Slot()
    def session_change(self):
        has_session: bool = core.has_session()
        self.refresh_action.set_enable(has_session)
        self.start_stop_action.set_can_enable()