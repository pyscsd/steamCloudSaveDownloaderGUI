from PySide6 import QtCore, QtGui, QtWidgets
from .core import core
import os
from .dialogs import login_dialog

class login_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Login")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.dialog = login_dialog()
        self.dialog.exec()

class logout_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Logout")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        if (os.path.isfile(core.s_session_file)):
            os.remove(core.s_session_file)

class session_menu(QtWidgets.QMenu):
    def __init__(self):
        super().__init__("Session")

        self.login_action = login_action()
        self.logout_action = logout_action()
        self.addAction(self.login_action)

        self.addAction(self.logout_action)
        self.aboutToShow.connect(self.on_menu_to_show)

    @QtCore.Slot()
    def on_menu_to_show(self):
        self.logout_action.setEnabled(os.path.isfile(core.s_session_file))

class options_menu(QtWidgets.QMenu):
    def __init__(self):
        super().__init__("Options")

class menu_bar(QtWidgets.QMenuBar):
    def __init__(self):
        super().__init__()
        self.session_menu = session_menu()
        self.options_menu = options_menu()
        self.addMenu(self.session_menu)
        self.addMenu(self.options_menu)