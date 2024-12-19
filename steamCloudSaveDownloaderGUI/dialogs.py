from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from .steamCloudSaveDownloader.steamCloudSaveDownloader.auth import auth
from .core import core
from . import data_provider
import pathlib
import os

class login_fail_message_box(QW.QMessageBox):
    def __init__(self):
        super().__init__(
            QW.QMessageBox.Icon.Critical,
            "Login Failed",
            "Failed to login. Please check if the inputs are correct.",
            QW.QMessageBox.StandardButton.Close)

class login_dialog(QW.QDialog):
    def __init__(self):
        super().__init__()
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
        auth_ = auth(core.s_config_dir, '')
        try:
            auth_.new_session(
                self.user_input.text(),
                self.password_input.text(),
                self.two_factor_input.text())
        except:
            fail_box = login_fail_message_box()
            fail_box.exec()
            return False
        return True

class options_dialog(QW.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")

        self.load_from_config_file()
        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

        self.setMinimumSize(600, 500)

    def load_from_config_file(self):
        self.config = data_provider.get_config_copy()

    def create_widgets(self):
        self.save_directory_label = QW.QLabel("Save directory:")
        self.save_directory_input = QW.QLineEdit()
        self.save_directory_input.setText(self.config['General']['save_dir'])
        self.save_directory_input.setFixedSize(300, self.save_directory_input.sizeHint().height())

        self.browse_button = QW.QToolButton()
        self.browse_button.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))

        self.rotation_label = QW.QLabel("Rotation:")
        self.rotation_value = QW.QSpinBox()
        self.rotation_value.setMinimum(1)
        self.rotation_value.setValue(self.config['Rotation']['rotation'])

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

        # TODO setRowStretch, setColStretch
        # https://stackoverflow.com/a/69884434

        self.main_vlayout.addWidget(self.button_box)

    @QtCore.Slot()
    def save(self):
        data_provider.commit(self.config)
        self.accept()

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

    def connect_signals(self):
        self.button_box.save_button.clicked.connect(self.save)
        self.button_box.cancel_button.clicked.connect(self.reject)
        self.browse_button.clicked.connect(self.browse)
        self.rotation_value.valueChanged.connect(self.on_rotation_value_change)
        self.log_level_value.valueChanged.connect(self.on_log_level_value_change)