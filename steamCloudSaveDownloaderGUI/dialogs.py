from PySide6 import QtCore, QtWidgets

class auth_dialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def create_widgets(self):
        self.user_label = QtWidgets.QLabel("Username:")
        self.user_input = QtWidgets.QLineEdit()
        self.password_label = QtWidgets.QLabel("Password:")
        self.password_input = QtWidgets.QLineEdit()
        self.two_factor_label = QtWidgets.QLabel("2FA (case insensitive):")
        self.two_factor_input = QtWidgets.QLineEdit()
        self.notice_label = QtWidgets.QLabel("NOTE: This program will not save your passwords locally.")

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.ok_button = self.button_box.addButton(
            "OK",
             QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.button_box.cancel_button = self.button_box.addButton(
            "Cancel",
             QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)

    def layout_widgets(self):
        right_align = QtCore.Qt.AlignmentFlag.AlignRight
        left_align = QtCore.Qt.AlignmentFlag.AlignLeft

        self.main_vlayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_vlayout)

        self.grid_layout = QtWidgets.QGridLayout()
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
        # TODO
        print("OK")
        self.accept()