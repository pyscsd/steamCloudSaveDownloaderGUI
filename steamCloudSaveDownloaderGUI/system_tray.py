from PySide6 import QtWidgets as QW
from PySide6 import QtCore, QtGui
from .res import icon

class show_action(QtGui.QAction):
    execute_signal = QtCore.Signal()
    def __init__(self):
        super().__init__(self.tr("Show"))
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.execute_signal.emit()

class quit_action(QtGui.QAction):
    execute_signal = QtCore.Signal()
    def __init__(self):
        super().__init__(self.tr("Quit"))
        self.triggered.connect(self.execute)

    @QtCore.Slot()
    def execute(self, p_action):
        self.execute_signal.emit()

class system_tray_menu(QW.QMenu):
    show_signal = QtCore.Signal()
    quit_signal = QtCore.Signal()

    def to_show(self):
        self.show_signal.emit()

    def to_quit(self):
        self.quit_signal.emit()

    def __init__(self):
        super().__init__()
        self.show_action = show_action()
        self.addAction(self.show_action)
        self.show_action.execute_signal.connect(self.to_show)

        self.quit_action = quit_action()
        self.addAction(self.quit_action)
        self.quit_action.execute_signal.connect(self.to_quit)

class system_tray(QW.QSystemTrayIcon):
    show_signal = QtCore.Signal()
    quit_signal = QtCore.Signal()

    def __init__(self, p_parent: QW.QMainWindow):
        super().__init__()
        self.main_window = p_parent
        self.setIcon(QtGui.QIcon(QtGui.QPixmap(":/scsd_256.jpg")))
        self.setToolTip("scsd-gui")
        self.menu = system_tray_menu()
        self.setContextMenu(self.menu)
        self.connect_signals()
        self.setVisible(True)

    def to_show(self):
        self.show_signal.emit()

    def to_quit(self):
        self.quit_signal.emit()

    def connect_signals(self):
        self.menu.show_signal.connect(self.to_show)
        self.menu.quit_signal.connect(self.to_quit)

    def show_hide_message(self):
        self.showMessage(
            self.tr("scsd-gui is now running in background"),
            "",
            QW.QSystemTrayIcon.MessageIcon.Information,
            3000)

    @QtCore.Slot()
    def download_complete(self):
        if self.main_window.isVisible() and not self.main_window.isMinimized():
            return
        self.showMessage(
            "scsd-gui",
            self.tr("Download Complete"),
            QW.QSystemTrayIcon.MessageIcon.Information,
            3000)