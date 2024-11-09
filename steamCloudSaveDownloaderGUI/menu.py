from PySide6 import QtCore, QtGui, QtWidgets

class login_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Login")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        pass

class logout_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Logout")
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        pass

class session_menu(QtWidgets.QMenu):
    def __init__(self):
        super().__init__("Session")

        self.login_action = login_action()
        self.logout_action = logout_action()
        self.addAction(self.login_action)

        # TODO: Disable if no session
        self.addAction(self.logout_action)

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