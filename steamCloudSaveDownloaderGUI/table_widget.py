from PySide6 import QtWidgets as QW
from PySide6 import QtCore
from .data_provider import data_provider

class table_model(QtCore.QAbstractTableModel):
    def __init__(self, p_parent:QtCore.QObject):
        self.parent = p_parent
        super().__init__(p_parent)
        self.raw_list = list()
        self.data_provider = data_provider()
        self.update_data(self.data_provider.load_existing_from_db())

    def rowCount(self, p_index: QtCore.QModelIndex):
        return len(self.raw_list)

    def columnCount(self, p_index: QtCore.QModelIndex):
        # Enabled, Preview(Capsule), appID, name, last updated
        return 5

    def flags(self, p_index: QtCore.QModelIndex):
        column = p_index.column()

        flags = super().flags(p_index)
        if column == 0:
            flags |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
            return flags
        else:
            return flags


    def data(self,
            p_index: QtCore.QModelIndex,
            p_role: QtCore.Qt.ItemDataRole):

        item = self.raw_list[p_index.row()]
        column = p_index.column()

        if p_role == QtCore.Qt.ItemDataRole.CheckStateRole:
            if column == 0:
                if self.data_provider.should_download_appid(item['app_id']):
                    return QtCore.Qt.CheckState.Checked
                else:
                    return QtCore.Qt.CheckState.Unchecked

        if p_role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        if column == 0:
            pass
        elif column == 1:
            # TODO: Pic
            return "Placeholder"
        elif column == 2:
            return item['app_id']
        elif column == 3:
            return item['name']
        elif column == 4:
            return "Placeholder"
        else:
            assert(False)

    def headerData(self,
                p_section: int,
                p_orient: QtCore.Qt.Orientation,
                p_role: QtCore.Qt.ItemDataRole):
        if p_orient == QtCore.Qt.Orientation.Horizontal and \
            p_role == QtCore.Qt.ItemDataRole.DisplayRole:
            if p_section == 0:
                return 'Enabled'
            elif p_section == 1:
                return 'Capsule'
            elif p_section == 2:
                return 'App ID'
            elif p_section == 3:
                return 'Name'
            elif p_section == 4:
                return 'Last Updated'
            else:
                assert(False)
        else:
            return super().headerData(p_section, p_orient, p_role)

    # Requires: [{'app_id': "value", 'name': "value"}]
    def update_data(self, p_list: list):
        self.beginResetModel()
        self.raw_list = p_list
        self.endResetModel()

        #start = self.createIndex(0, 0)
        #end = self.createIndex(self.rowCount(self.parent) - 1, self.columnCount(self.parent) - 1)
        #self.dataChanged.emit(start, end)

class table_sort_filter_proxy(QtCore.QSortFilterProxyModel):
    def __init__(self, p_parent:QtCore.QObject):
        super().__init__(p_parent)


class table_view(QW.QTableView):
    def __init__(self, p_parent:QtCore.QObject):
        super().__init__(p_parent)
        self.setMinimumSize(800, 400)

        self.verticalHeader().hide()

        self.setSelectionBehavior(
            QW.QAbstractItemView.SelectionBehavior.SelectRows)

        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)

    def set_header_stretch(self, p_section_size:int):
        for i in range(p_section_size - 1):
            self.horizontalHeader().setSectionResizeMode(
                i,
                QW.QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            p_section_size - 1,
            QW.QHeaderView.ResizeMode.Stretch)


class table_widget(QW.QWidget):
    def __init__(self, p_parent: QtCore.QObject):
        super().__init__(p_parent)

        self.table_view = table_view(self)
        self.table_model = table_model(self)
        self.sort_filter_model = table_sort_filter_proxy(self)

        self.sort_filter_model.setSourceModel(self.table_model)
        self.table_view.setModel(self.sort_filter_model)

        self.table_view.set_header_stretch(self.table_model.columnCount(None))
        self.sort_filter_model.sort(2, QtCore.Qt.SortOrder.AscendingOrder)

        self.v_layout = QW.QVBoxLayout(self)
        self.v_layout.addWidget(self.table_view)

        # TODO: On press load
        #game_list = data_provider_.get_game_list_from_web()

    @QtCore.Slot(list)
    def on_data_change(self, p_data: list):
        self.table_model.update_data(p_data)