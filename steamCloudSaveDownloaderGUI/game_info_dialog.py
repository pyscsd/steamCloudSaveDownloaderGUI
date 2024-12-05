from PySide6 import QtCore, QtGui
from PySide6 import QtWidgets as QW
from . import data_provider

from enum import Enum
from operator import itemgetter
import os
import platform
import webbrowser
import pprint # TODO Remove

class item_type_e(Enum):
    dir_type = 0
    file_type = 1
    version_type = 2

class tree_model(QtGui.QStandardItemModel):
    item_type_role = QtCore.Qt.ItemDataRole.UserRole + 1
    file_id_role = QtCore.Qt.ItemDataRole.UserRole + 2
    revision_loaded_role = QtCore.Qt.ItemDataRole.UserRole + 3
    versioned_name_role = QtCore.Qt.ItemDataRole.UserRole + 4

    header_labels = ["Name/Version", "Date Written"]
    column_count = len(header_labels)

    def __init__(self, p_parent:QtCore.QObject, p_app_id: int):
        super().__init__(p_parent)
        self.setHorizontalHeaderLabels(tree_model.header_labels)
        self.app_id = p_app_id
        self.file_icon = QW.QFileIconProvider().icon(QW.QFileIconProvider.IconType.File)
        self.dir_icon = QW.QFileIconProvider().icon(QW.QFileIconProvider.IconType.Folder)
        self.setup_directories_and_files()


    def create_directory_item(self, p_directory_name: str) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem(self.dir_icon, p_directory_name)
        item.setColumnCount(tree_model.column_count)
        item.setData(item_type_e.dir_type, tree_model.item_type_role)
        item.setEditable(False)
        item.setCheckable(False)
        return item

    def create_file_item(self, p_file_name: str, p_file_id: int) -> QtGui.QStandardItem:
        item = QtGui.QStandardItem(
            self.file_icon,
            p_file_name)
        item.setColumnCount(tree_model.column_count)
        item.setEditable(False)
        item.setCheckable(False)
        item.setData(item_type_e.file_type, tree_model.item_type_role)
        item.setData(p_file_id, tree_model.file_id_role)
        item.setData(False, tree_model.revision_loaded_role)

        placeholder_item = QtGui.QStandardItem("Placeholder")
        placeholder_item.setData(item_type_e.version_type, tree_model.item_type_role)
        item.appendRow(placeholder_item)

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

    def populate_file_version(self, p_item: QtGui.QStandardItem):
        if p_item.rowCount() != 0:
            p_item.removeRows(0, p_item.rowCount())
        file_id: int = p_item.data(tree_model.file_id_role)

        file_name = p_item.text()

        version_info = data_provider.get_file_version_by_file_id(file_id)
        for version_date, version_num in version_info:
            versioned_name = f"{file_name}.scsd_{version_num}"
            name_item = QtGui.QStandardItem(f"Ver.{version_num} ({versioned_name})")
            name_item.setData(item_type_e.version_type, tree_model.item_type_role)
            name_item.setData(versioned_name, tree_model.versioned_name_role)
            name_item.setCheckable(False)
            name_item.setEditable(False)

            version_date_item = QtGui.QStandardItem(str(version_date))
            version_date_item.setData(item_type_e.version_type, tree_model.item_type_role)
            version_date_item.setData(versioned_name, tree_model.versioned_name_role)
            version_date_item.setCheckable(False)
            version_date_item.setEditable(False)

            p_item.appendRow([name_item, version_date_item])
        p_item.setData(True, tree_model.revision_loaded_role)

    def on_item_expanded(self, p_index: QtCore.QModelIndex):
        item: QtGui.QStandardItem = self.itemFromIndex(p_index)

        item_type: item_type_e = item.data(tree_model.item_type_role)
        list_loaded: bool = item.data(tree_model.revision_loaded_role)

        if item_type != item_type_e.file_type:
            return

        if list_loaded:
            return

        self.populate_file_version(item)

    def open_file_location(self, p_index: QtCore.QModelIndex):
        location_list = []
        item = self.itemFromIndex(p_index)
        if item.data(tree_model.item_type_role) == item_type_e.version_type:
            location_list.append(item.data(tree_model.versioned_name_role))
            item = item.parent() # Skip file name part
        elif item.data(tree_model.item_type_role) == item_type_e.dir_type:
            location_list.append(item.text())
        while True:
            parent = item.parent()
            if parent is None:
                break
            if parent.text() != '/':
                location_list.append(parent.text())
            item = parent

        location_list.append(str(self.app_id))
        location_list.append(data_provider.config['General']['save_dir'])
        location_list.reverse()

        location = os.path.join(*location_list)

        if os.path.isdir(location):
            webbrowser.open("file:///" + str(location))
        elif os.path.isfile(location):
            if platform.system() == "Windows":
                import subprocess
                subprocess.Popen('explorer /select,"' + str(location) + '"')
            else:
                print("TODO")
        else:
            print(f" {location} not exist")
            return

class open_saves_directory_action(QtGui.QAction):
    def __init__(self,
                p_model: tree_model,
                p_index: QtCore.QModelIndex):
        super().__init__("Open File Location")

        self.model = p_model
        self.index = p_index
        self.triggered.connect(self.execute)

    @QtCore.Slot(bool)
    def execute(self, p_b: bool):
        self.model.open_file_location(self.index)

class tree_csm(QW.QMenu):
    def __init__(self,
                p_parent: QW.QWidget,
                p_model: tree_model,
                p_index: QtCore.QModelIndex):
        super().__init__(p_parent)
        self.open_location_action = open_saves_directory_action(p_model, p_index)
        self.addAction(self.open_location_action)

class tree_view(QW.QTreeView):
    def __init__(
            self,
            p_parent:QtCore.QObject,
            p_model: QtGui.QStandardItemModel):
        super().__init__(p_parent)
        self.setModel(p_model)
        self.setMinimumSize(800, 400)
        self.setRootIndex(self.model().invisibleRootItem().child(0, 0).index())

        self.expanded.connect(self.on_item_expanded)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_csm_requested)

        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QW.QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(1, QW.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setMinimumSectionSize(120)

    @QtCore.Slot(QtCore.QPoint)
    def on_csm_requested(self, p_point: QtCore.QPoint):
        index = self.indexAt(p_point)

        menu = tree_csm(self, self.model(), index)
        menu.popup(self.viewport().mapToGlobal(p_point))

    @QtCore.Slot(QtCore.QModelIndex)
    def on_item_expanded(self, p_index: QtCore.QModelIndex):
        self.model().on_item_expanded(p_index)


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
        self.tree_view = tree_view(self, self.tree_model)

    def layout_widgets(self):
        self.v_layout = QW.QVBoxLayout(self)
        self.v_layout.addWidget(self.tree_view)

    def connect_signals(self):
        pass