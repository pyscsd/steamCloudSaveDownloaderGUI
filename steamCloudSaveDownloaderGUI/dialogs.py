from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from .steamCloudSaveDownloader.steamCloudSaveDownloader.auth import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger
from .core import core
from . import data_provider
from .res import icon
from .status_bar import status_bar
import os
import pathlib
import traceback

class login_fail_message_box(QW.QMessageBox):
    def __init__(self):
        super().__init__(
            QW.QMessageBox.Icon.Critical,
            "Login Failed",
            "Failed to login. Please check if the inputs are correct.",
            QW.QMessageBox.StandardButton.Close)

class login_dialog(QW.QDialog):
    def __init__(self, p_status_bar: status_bar):
        super().__init__()
        self.status_bar = p_status_bar
        self.setWindowTitle("Login")

        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def create_widgets(self):
        input_size = 120

        self.user_label = QW.QLabel("Username:")
        self.user_input = QW.QLineEdit()
        self.user_input.setFixedSize(input_size, self.user_input.sizeHint().height())

        self.password_label = QW.QLabel("Password:")
        self.password_input = QW.QLineEdit()
        self.password_input.setEchoMode(QW.QLineEdit.EchoMode.Password)
        self.password_input.setFixedSize(input_size, self.password_input.sizeHint().height())

        self.two_factor_label = QW.QLabel("2FA (case insensitive):")
        self.two_factor_input = QW.QLineEdit()
        self.two_factor_input.setFixedSize(input_size, self.two_factor_input.sizeHint().height())

        self.notice_label = QW.QLabel("NOTE: This program will not save your passwords locally.")

        self.button_box = QW.QDialogButtonBox(self)
        self.button_box.ok_button = self.button_box.addButton(
            "OK",
             QW.QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.cancel_button = self.button_box.addButton(
            "Cancel",
             QW.QDialogButtonBox.ButtonRole.RejectRole)

    def layout_widgets(self):
        right_align = QtCore.Qt.AlignmentFlag.AlignRight
        left_align = QtCore.Qt.AlignmentFlag.AlignLeft

        self.main_vlayout = QW.QVBoxLayout()
        self.setLayout(self.main_vlayout)

        self.grid_layout = QW.QGridLayout()
        self.main_vlayout.addLayout(self.grid_layout)

        self.grid_layout.addWidget(self.user_label, 0, 0, right_align)
        self.grid_layout.addWidget(self.user_input, 0, 1, left_align)
        self.grid_layout.addWidget(self.password_label, 1, 0, right_align)
        self.grid_layout.addWidget(self.password_input, 1, 1, left_align)
        self.grid_layout.addWidget(self.two_factor_label, 2, 0, right_align)
        self.grid_layout.addWidget(self.two_factor_input, 2, 1, left_align)
        self.grid_layout.addWidget(self.notice_label, 3, 0, 1, 2, left_align)

        self.main_vlayout.addWidget(self.button_box)

    def connect_signals(self):
        self.button_box.ok_button.clicked.connect(self.ok)
        self.button_box.cancel_button.clicked.connect(self.reject)

    @QtCore.Slot()
    def ok(self):
        if not self.check_input_validity():
            return
        if self.login():
            self.accept()

    def set_style_based_on_validity(self, p_line_edit:QW.QLineEdit) -> bool:
        if len(p_line_edit.text()) == 0:
            p_line_edit.setStyleSheet("border: 1px solid red")
            return False
        else:
            p_line_edit.setStyleSheet("")
            return True

    def check_input_validity(self) -> bool:
        user = self.set_style_based_on_validity(self.user_input)
        password = self.set_style_based_on_validity(self.password_input)
        two_factor = self.set_style_based_on_validity(self.two_factor_input)

        return user and password and two_factor

    def login(self) -> bool:
        self.status_bar.set_authenticating()
        auth_ = auth(core.s_config_dir, '')
        try:
            auth_.new_session(
                self.user_input.text(),
                self.password_input.text(),
                self.two_factor_input.text())
        except Exception as e:
            ec = traceback.format_exc()
            logger.error(ec)
            fail_box = login_fail_message_box()
            fail_box.exec()
            return False
        return True

class options_dialog(QW.QDialog):
    config_reloaded_signal = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")

        self.load_from_config_file()
        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def load_from_config_file(self):
        self.config = data_provider.get_config_copy()

    def create_widgets(self):
        self.save_directory_label = QW.QLabel("Save directory:")
        self.save_directory_input = QW.QLineEdit()
        self.save_directory_input.setText(self.config['General']['save_dir'])
        self.save_directory_input.setFixedSize(300, self.save_directory_input.sizeHint().height())
        save_directory_help = "Where to save the saves"
        self.save_directory_label.setToolTip(save_directory_help)
        self.save_directory_input.setToolTip(save_directory_help)

        self.browse_button = QW.QToolButton()
        self.browse_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))
        self.browse_button.setToolTip("Open File Explorer")

        self.rotation_label = QW.QLabel("Save Rotation:")
        self.rotation_value = QW.QSpinBox()
        self.rotation_value.setMinimum(1)
        self.rotation_value.setValue(self.config['Rotation']['rotation'])
        rotation_help = "The number of versions to keep locally. The older ones will have suffix '.scsd_X' append to the original file name."
        self.rotation_label.setToolTip(rotation_help)
        self.rotation_value.setToolTip(rotation_help)

        self.button_box = QW.QDialogButtonBox(self)
        self.button_box.save_button = self.button_box.addButton(
            "Save",
             QW.QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.cancel_button = self.button_box.addButton(
            "Cancel",
             QW.QDialogButtonBox.ButtonRole.RejectRole)

        self.log_level_label = QW.QLabel("Log Level:")
        self.log_level_value = QW.QSpinBox()
        self.log_level_value.setMinimum(0)
        self.log_level_value.setMaximum(3)
        self.log_level_value.setValue(self.config['Log']['log_level'])
        log_level_help = "How detail should the log be.\n0: Show Error messages only\n1: Show Error and Warning messages only\n2: Show Error, Warning and Info messages only\n3: Show Error, Warning, Info and Debug messages"
        self.log_level_label.setToolTip(log_level_help)
        self.log_level_value.setToolTip(log_level_help)

        self.auto_start_label = QW.QLabel("Auto Start on Startup:")
        self.auto_start = QW.QCheckBox()
        self.auto_start.setChecked(self.config['GUI']['auto_start'])
        auto_start_help = "If the program should auto start on startup"
        self.auto_start_label.setToolTip(auto_start_help)
        self.auto_start.setToolTip(auto_start_help)

        self.minimize_to_tray_label = QW.QLabel("Minimize to Tray:")
        self.minimize_to_tray = QW.QCheckBox()
        self.minimize_to_tray.setChecked(self.config['GUI']['minimize_to_tray'])
        minimize_to_tray_help = "Minimize to system tray instead of close"
        self.minimize_to_tray_label.setToolTip(minimize_to_tray_help)
        self.minimize_to_tray.setToolTip(minimize_to_tray_help)

        self.download_interval_label = QW.QLabel("Auto Download Interval (Minutes):")
        self.download_interval_spinbox = QW.QSpinBox()
        self.download_interval_spinbox.setMinimum(0)
        self.download_interval_spinbox.setMaximum(10000)
        self.download_interval_spinbox.setValue(self.config['GUI']['download_interval'])
        download_interval_help = "The interval in minutes between each auto download"
        self.download_interval_label.setToolTip(download_interval_help)
        self.download_interval_spinbox.setToolTip(download_interval_help)

        self.help_icon_label = QW.QLabel()
        help_icon = QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DialogQuestion)
        self.help_icon_label.setPixmap(help_icon.pixmap(help_icon.actualSize(QtCore.QSize(24, 24))))
        self.help_label = QW.QLabel("Hover onto options for description")

    def layout_widgets(self):
        right_align = QtCore.Qt.AlignmentFlag.AlignRight
        left_align = QtCore.Qt.AlignmentFlag.AlignLeft

        self.main_vlayout = QW.QVBoxLayout()
        self.setLayout(self.main_vlayout)

        self.grid_layout = QW.QGridLayout()
        self.main_vlayout.addLayout(self.grid_layout)
        self.grid_layout.addWidget(self.save_directory_label, 0, 0, right_align)
        self.grid_layout.addWidget(self.save_directory_input, 0, 1, left_align)
        self.grid_layout.addWidget(self.browse_button, 0, 2, left_align)
        self.grid_layout.addWidget(self.rotation_label, 1, 0, right_align)
        self.grid_layout.addWidget(self.rotation_value, 1, 1, left_align)
        self.grid_layout.addWidget(self.log_level_label, 2, 0, right_align)
        self.grid_layout.addWidget(self.log_level_value, 2, 1, left_align)
        self.grid_layout.addWidget(self.auto_start_label, 3, 0, right_align)
        self.grid_layout.addWidget(self.auto_start, 3, 1, left_align)
        self.grid_layout.addWidget(self.minimize_to_tray_label, 4, 0, right_align)
        self.grid_layout.addWidget(self.minimize_to_tray, 4, 1, left_align)
        self.grid_layout.addWidget(self.download_interval_label, 5, 0, right_align)
        self.grid_layout.addWidget(self.download_interval_spinbox, 5, 1, left_align)
        self.grid_layout.addWidget(self.help_icon_label, 6, 0, right_align)
        self.grid_layout.addWidget(self.help_label, 6, 1, left_align)


        # TODO setRowStretch, setColStretch
        # https://stackoverflow.com/a/69884434

        self.main_vlayout.addStretch()
        self.main_vlayout.addWidget(self.button_box)

    @QtCore.Slot()
    def save(self):
        data_provider.commit(self.config)
        self.accept()
        self.config_reloaded_signal.emit()

    @QtCore.Slot()
    def browse(self):
        self.file_dialog = QW.QFileDialog()
        self.file_dialog.setDirectory(self.save_directory_input.text())
        self.file_dialog.setFileMode(QW.QFileDialog.FileMode.Directory)
        self.file_dialog.accepted.connect(self.browse_accept)

        self.file_dialog.exec()

    @QtCore.Slot()
    def browse_accept(self):
        qdir = self.file_dialog.directory()
        file_list = self.file_dialog.selectedFiles()
        if (len(file_list) == 0):
            path = str(pathlib.Path(qdir.absolutePath()))
        else:
            path = str(file_list[0])
        path = os.path.normpath(path)
        self.save_directory_input.setText(path)
        self.config['General']['save_dir'] = path

    @QtCore.Slot()
    def on_rotation_value_change(self, p_value: int):
        self.config['Rotation']['rotation'] = p_value

    @QtCore.Slot()
    def on_log_level_value_change(self, p_value: int):
        self.config['Log']['log_level'] = p_value

    @QtCore.Slot(bool)
    def on_auto_start_change(self, p_value: bool):
        self.config['GUI']['auto_start'] = p_value

    @QtCore.Slot(bool)
    def on_minimize_to_tray_change(self, p_value: bool):
        self.config['GUI']['minimize_to_tray'] = p_value

    @QtCore.Slot(int)
    def on_download_interval_change(self, p_value: int):
        self.config['GUI']['download_interval'] = p_value

    def connect_signals(self):
        self.button_box.save_button.clicked.connect(self.save)
        self.button_box.cancel_button.clicked.connect(self.reject)
        self.browse_button.clicked.connect(self.browse)
        self.rotation_value.valueChanged.connect(self.on_rotation_value_change)
        self.log_level_value.valueChanged.connect(self.on_log_level_value_change)
        self.auto_start.toggled.connect(self.on_auto_start_change)
        self.minimize_to_tray.toggled.connect(self.on_minimize_to_tray_change)
        self.download_interval_spinbox.valueChanged.connect(self.on_download_interval_change)

class about_dialog(QW.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")

        self.set_icon()
        self.set_version()
        self.set_repo()
        self.set_author()
        self.set_submit_issue()
        self.set_disclaimer()
        self.set_license()
        self.set_button_box()
        self.layout_widgets()
        # TODO: Version
        # TODO: Size Hint

    def layout_widgets(self):
        self.main_vlayout = QW.QVBoxLayout()
        self.setLayout(self.main_vlayout)

        self.icon_layout = QW.QHBoxLayout()
        self.icon_layout.addStretch()
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addStretch()
        self.main_vlayout.addLayout(self.icon_layout)

        self.version_layout = QW.QHBoxLayout()
        self.version_layout.addStretch()
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addStretch()
        self.main_vlayout.addLayout(self.version_layout)

        self.repo_layout = QW.QHBoxLayout()
        self.repo_layout.addStretch()
        self.repo_layout.addWidget(self.repo_label)
        self.repo_layout.addStretch()
        self.main_vlayout.addLayout(self.repo_layout)

        self.author_layout = QW.QHBoxLayout()
        self.author_layout.addStretch()
        self.author_layout.addWidget(self.author_label)
        self.author_layout.addStretch()
        self.main_vlayout.addLayout(self.author_layout)

        self.issue_layout = QW.QHBoxLayout()
        self.issue_layout.addStretch()
        self.issue_layout.addWidget(self.issue_label)
        self.issue_layout.addStretch()
        self.main_vlayout.addLayout(self.issue_layout)

        self.license_layout = QW.QHBoxLayout()
        self.license_layout.addStretch()
        self.license_layout.addWidget(self.license_label)
        self.license_layout.addStretch()
        self.main_vlayout.addLayout(self.license_layout)

        self.disclaimer_layout = QW.QHBoxLayout()
        self.disclaimer_layout.addStretch()
        self.disclaimer_layout.addWidget(self.disclaimer_label)
        self.disclaimer_layout.addStretch()
        self.main_vlayout.addLayout(self.disclaimer_layout)

        self.button_box_layout = QW.QHBoxLayout()
        self.button_box_layout.addStretch()
        self.button_box_layout.addWidget(self.button_box)
        self.button_box_layout.addStretch()
        self.main_vlayout.addLayout(self.button_box_layout)

    def set_icon(self):
        self.icon_label = QW.QLabel()
        pixmap = QtGui.QPixmap(":/scsd_256.jpg")
        pixmap = pixmap.scaled(128, 128)
        self.icon_label.setPixmap(pixmap)

    def set_version(self):
        self.version_label = QW.QLabel("Version: x.x.x")

    def set_repo(self):
        self.repo_label = QW.QLabel("<a href='https://github.com/pyscsd/steamCloudSaveDownloaderGUI'>pyscsd/steamCloudSaveDownloaderGUI</a>")
        self.repo_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.repo_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.repo_label.setOpenExternalLinks(True)

    def set_author(self):
        self.author_label = QW.QLabel("Author: <a href='https://github.com/hhhhhojeihsu'>hhhhhojeihsu</a>")
        self.author_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.author_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.author_label.setOpenExternalLinks(True)

    def set_submit_issue(self):
        self.issue_label = QW.QLabel("<a href='https://github.com/pyscsd/steamCloudSaveDownloader/issues'>Submit Issue</a>")
        self.issue_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.issue_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.issue_label.setOpenExternalLinks(True)

    def set_license(self):
        self.license_label = QW.QLabel("Released under MIT License")

    def set_disclaimer(self):
        self.disclaimer_label = QW.QLabel("This program is not affiliated with Valve or Steam.\nSteam is a trademark of Valve Corporation.")

    def set_button_box(self):
        self.button_box = QW.QDialogButtonBox(self)
        self.button_box.close_button = self.button_box.addButton(
            "Close",
             QW.QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.close_button.clicked.connect(self.accept)