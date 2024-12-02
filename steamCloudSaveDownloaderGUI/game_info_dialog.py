from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from . import data_provider

from operator import itemgetter
import pprint # TODO Remove

class tree_model(QtGui.QStandardItemModel):
    file_id_role = QtCore.Qt.ItemDataRole.UserRole + 1

    def __init__(self, p_parent:QtCore.QObject, p_app_id: int):
        super().__init__(p_parent)
        self.app_id = p_app_id
        self.file_icon = QW.QFileIconProvider().icon(QW.QFileIconProvider.IconType.File)
        self.dir_icon = QW.QFileIconProvider().icon(QW.QFileIconProvider.IconType.Folder)
        self.setup_directories_and_files()

    def create_directory_item(self, p_directory_name: str) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem(self.dir_icon, p_directory_name)
        item.setEditable(False)
        item.setCheckable(False)
        return item

    def create_file_item(self, p_file_name: str, p_file_id: int) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem(
            self.file_icon,
            p_file_name)
        item.setEditable(False)
        item.setCheckable(False)
        item.setData(self.file_id_role, p_file_id)
        return item

    def setup_directories_and_files(self):
        #file_id, filename, location
        sorted_by_location_filename = \
            sorted(data_provider.get_files_from_app_id(self.app_id), key=itemgetter(2, 1))

        # Dictionary hierarchy, each node is a folder/item
        # Directory and file cannot be same name in Windows/Linux
        actual_root = self.create_directory_item('/')
        self.invisibleRootItem().appendRow(actual_root)
        self.hierarchy_dict = {'/': {'.': actual_root}}
        for file_id, filename, location in sorted_by_location_filename:
            print(f'{location} :: {filename}')
            current_node = self.hierarchy_dict['/']
            if len(location) != 0:
                for level in location.split('/'):
                    if level not in current_node:
                        dir_item = self.create_directory_item(level)
                        current_node[level] = {'.': dir_item}
                        current_node['.'].appendRow(dir_item)
                    current_node = current_node[level]

            file_item = self.create_file_item(filename, file_id)
            current_node[filename] = {'.': file_item}
            current_node['.'].appendRow(file_item)

class tree_view(QW.QTreeView):
    def __init__(self, p_parent:QtCore.QObject):
        super().__init__(p_parent)
        self.setMinimumSize(800, 400)

class game_info_dialog(QW.QDialog):
    def __init__(self, p_app_id: int, game_name: str):
        super().__init__()

        self.setWindowTitle(f"{game_name} Saves")
        self.app_id = p_app_id

        self.create_widgets()
        self.layout_widgets()
        self.connect_signals()

    def create_widgets(self):
        self.tree_model = tree_model(self, self.app_id)
        self.tree_view = tree_view(self)
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(self.tree_model.invisibleRootItem().child(0, 0).index())

    def layout_widgets(self):
        self.v_layout = QW.QVBoxLayout(self)
        self.v_layout.addWidget(self.tree_view)

    def connect_signals(self):
        pass