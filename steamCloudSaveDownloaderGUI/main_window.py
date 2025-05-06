from PySide6 import QtWidgets as QW
from PySide6 import QtGui, QtCore
from . import data_provider
from . import menu
from . import status_bar
from . import system_tray
from . import table_widget
from .translator import reload_translator

class exit_dialog(QW.QMessageBox):
    def __init__(self):
        super().__init__(
            QW.QMessageBox.Icon.NoIcon,
            self.tr("Close in progress"),
            self.tr("Please wait for the program to close gracefully."))


class main_window(QW.QMainWindow):
    def __init__(self):
        super().__init__()

        reload_translator()

        self.confirm_quit = False

        self.system_tray = system_tray.system_tray(self)

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
        self.menu_bar.refresh_action.data_updated_signal.connect(self.table_widget.refresh)

        self.menu_bar.download_action.row_updated_signal.connect(self.table_widget.on_app_id_change)
        self.menu_bar.download_action.download_started_signal.connect(self.table_widget.download_started)
        self.menu_bar.download_action.download_complete_signal.connect(self.system_tray.download_complete)
        self.menu_bar.download_action.download_complete_signal.connect(self.table_widget.download_complete)

        self.menu_bar.quit_action.quit_signal.connect(self.formal_quit)

        self.menu_bar.downloader_timer.row_updated_signal.connect(self.table_widget.on_app_id_change)
        self.menu_bar.downloader_timer.download_started_signal.connect(self.table_widget.download_started)
        self.menu_bar.downloader_timer.download_complete_signal.connect(self.system_tray.download_complete)
        self.menu_bar.downloader_timer.download_complete_signal.connect(self.table_widget.download_complete)

        self.system_tray.activated.connect(self.system_tray_activated)
        self.system_tray.show_signal.connect(self.show)
        self.system_tray.quit_signal.connect(self.formal_quit)

    def finalize(self):
        self.exit_dialog.show()
        self.table_widget.on_main_window_closed()
        self.menu_bar.download_action.stop_download()
        self.menu_bar.downloader_timer.stop_download()
        self.exit_dialog.close()

    def closeEvent(self, p_close_event: QtGui.QCloseEvent):
        if (data_provider.config['GUI']['minimize_to_tray'] and not self.confirm_quit):
            p_close_event.ignore()
            self.hide()
            self.system_tray.show_hide_message()
            return
        self.finalize()
        super().closeEvent(p_close_event)

    @QtCore.Slot()
    def formal_quit(self):
        self.confirm_quit = True
        self.close()

    @QtCore.Slot(QW.QSystemTrayIcon.ActivationReason)
    def system_tray_activated(self, p_reason: QW.QSystemTrayIcon.ActivationReason):
        if p_reason == QW.QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()