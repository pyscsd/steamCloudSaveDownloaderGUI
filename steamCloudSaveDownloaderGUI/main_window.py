from PySide6 import QtWidgets as QW
from PySide6 import QtGui
from . import menu
from . import status_bar
from . import table_widget

class exit_dialog(QW.QMessageBox):
    def __init__(self):
        super().__init__(
            QW.QMessageBox.Icon.Information,
            "Close in progress",
            "Please wait for the program to close gracefully.")


class main_window(QW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.status_bar = status_bar.status_bar()
        self.setStatusBar(self.status_bar)

        self.menu_bar = menu.menu_bar(self, self.status_bar)
        self.setMenuBar(self.menu_bar)

        self.table_widget = table_widget.table_widget(self, self.status_bar)
        self.setCentralWidget(self.table_widget)

        self.setWindowTitle("scsd-gui")

        self.connect_signals()
        self.exit_dialog = exit_dialog()


    def connect_signals(self):
        self.menu_bar.refresh_action.data_updated_signal.connect(self.table_widget.on_data_change)

    def closeEvent(self, p_close_event: QtGui.QCloseEvent):
        self.exit_dialog.show()
        self.table_widget.on_main_window_closed()
        self.menu_bar.download_action.on_main_window_closed()
        self.menu_bar.download_all_action.on_main_window_closed()
        self.exit_dialog.close()