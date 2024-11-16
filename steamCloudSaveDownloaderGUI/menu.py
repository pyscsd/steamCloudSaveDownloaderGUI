from PySide6 import QtCore, QtGui, QtWidgets
from .core import core
import os
from .dialogs import login_dialog, options_dialog

class login_action(QtGui.QAction):
    login_success_signal = QtCore.Signal()

    def __init__(self):
        super().__init__("Login")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.dialog = login_dialog()
        result:QtWidgets.QDialog.DialogCode = self.dialog.exec()

        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.login_success_signal.emit()

class logout_action(QtGui.QAction):
    logout_signal = QtCore.Signal()
    def __init__(self):
        super().__init__("Logout")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        if (os.path.isfile(core.s_session_file)):
            os.remove(core.s_session_file)
            self.logout_signal.emit()

class session_menu(QtWidgets.QMenu):
    login_success_signal = QtCore.Signal()
    logout_signal = QtCore.Signal()

    def __init__(self):
        super().__init__("Session")

        self.login_action = login_action()
        self.logout_action = logout_action()
        self.addAction(self.login_action)

        self.addAction(self.logout_action)
        self.aboutToShow.connect(self.on_menu_to_show)
        self.login_action.login_success_signal.connect(self.login_success)
        self.logout_action.logout_signal.connect(self.logout_complete)

    @QtCore.Slot()
    def on_menu_to_show(self):
        self.logout_action.setEnabled(os.path.isfile(core.s_session_file))

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

class start_stop_action(QtGui.QAction):
    def __init__(self):
        super().__init__()
        self.start_state = True
        self.triggered.connect(self.execute)
        self.set_text()
        self.set_can_enable()

    def set_can_enable(self):
        has_session:bool = os.path.isfile(core.s_session_file)
        self.setEnabled(has_session)

        if not has_session:
            self.start_state = True
        self.set_text()

    def set_text(self):
        if self.start_state:
            self.setText("Start")
        else:
            self.setText("Stop")

    @QtCore.Slot()
    def execute(self, p_action):
        if self.start_state:
            self.start_state = False
        else:
            self.start_state = True
        self.set_text()

class menu_bar(QtWidgets.QMenuBar):
    def __init__(self):
        super().__init__()
        self.session_menu = session_menu()
        self.options_action = options_action()
        self.start_stop_action = start_stop_action()
        self.addMenu(self.session_menu)
        self.addAction(self.options_action)
        self.addAction(self.start_stop_action)

        self.connect_signals()

    def connect_signals(self):
        self.session_menu.login_success_signal.connect(self.session_change)
        self.session_menu.logout_signal.connect(self.session_change)

    @QtCore.Slot()
    def session_change(self):
        self.start_stop_action.set_can_enable()