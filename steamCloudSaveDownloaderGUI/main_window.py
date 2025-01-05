from PySide6 import QtWidgets, QtGui
from . import menu
from . import status_bar
from . import table_widget

class main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.status_bar = status_bar.status_bar()
        self.setStatusBar(self.status_bar)

        self.menu_bar = menu.menu_bar(self, self.status_bar)
        self.setMenuBar(self.menu_bar)

        self.table_widget = table_widget.table_widget(self)
        self.setCentralWidget(self.table_widget)

        self.setWindowTitle("scsd-gui")

        self.connect_signals()

    def connect_signals(self):
        self.menu_bar.start_stop_action.data_updated_signal.connect(self.table_widget.on_data_change)
        self.menu_bar.refresh_action.data_updated_signal.connect(self.table_widget.on_data_change)

    def closeEvent(self, p_close_event: QtGui.QCloseEvent):
        self.table_widget.on_main_window_closed()