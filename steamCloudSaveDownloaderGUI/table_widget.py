from PySide6 import QtWidgets as QW
from PySide6 import QtCore, QtGui
from .core import core
from . import data_provider
from . import status_bar
from . import thread_controller
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger
from .game_info_dialog import game_info_dialog

import os
import requests
import shutil
import time
import webbrowser

# Return 0 if not checked yet
# Retrun 1 if 404
# Retrun 2 if found
def game_header_availible(p_app_id: int) -> int:
    header_name = f'{p_app_id}.jpg'
    cached_image_location = os.path.join(core.s_cache_header_dir, header_name)

    if os.path.isfile(cached_image_location):
        return 2

    not_availible_header_name = f'{p_app_id}.404'
    not_availible_cached_image_location = os.path.join(core.s_cache_header_dir, not_availible_header_name)

    if os.path.isfile(not_availible_cached_image_location):
        return 1
    return 0

class game_header_downloader(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)
    def __init__(self, p_app_id_list: list):
        super().__init__()
        self.app_id_list = p_app_id_list

    def check_interrupt(self):
        interrupt = QtCore.QThread.currentThread().isInterruptionRequested()
        if interrupt:
            logger.debug("(game_header_downloader) interrupt recieved")
        return interrupt


    @QtCore.Slot()
    def do_job(self):
        for app_id in self.app_id_list:
            if self.check_interrupt():
                break

            # Return 0 if not checked yet
            # Retrun 1 if 404
            # Retrun 2 if found
            if game_header_availible(app_id) != 0:
                continue

            logger.debug(f"(game_header_downloader) download {app_id}")
            if self.download_game_header_image(app_id):
                self.notification.emit(app_id)

            # Increase responsive
            for i in range(3):
                if self.check_interrupt():
                    break
                time.sleep(1)
            else:
                continue
            break

        logger.debug("(game_header_downloader) download complete")
        self.result_ready.emit()
        QtCore.QThread.currentThread().quit()

    # Return true, if notification required, false if not
    def download_game_header_image(self, p_app_id: int) -> bool:
        url_prefix = 'https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/'

        header_link = f'{url_prefix}/{p_app_id}/header.jpg'

        header_name = f'{p_app_id}.jpg'
        cached_image_location = os.path.join(core.s_cache_header_dir, header_name)

        if os.path.isfile(cached_image_location):
            return 2

        not_availible_header_name = f'{p_app_id}.404'
        not_availible_cached_image_location = os.path.join(core.s_cache_header_dir, not_availible_header_name)

        with requests.Session().get(header_link, stream=True) as r:
            if r.status_code == 404:
                with open(not_availible_cached_image_location, 'a'):
                    pass

            if r.status_code != 200:
                return False

            with open(cached_image_location, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return True

class table_refresher(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)
    set_status_bar_text = QtCore.Signal(str)
    set_status_bar_percent = QtCore.Signal(int)

    def __init__(self, p_table_widget):
        super().__init__()
        self.table_widget = p_table_widget

    def check_interrupt(self):
        interrupt = QtCore.QThread.currentThread().isInterruptionRequested()
        if interrupt:
            pass

    @QtCore.Slot()
    def do_job(self):
        self.set_status_bar_text.emit("Refreshing...")
        self.set_status_bar_percent.emit(30)

        self.table_widget.table_model.update_data(data_provider.load_from_db_and_web())

        self.set_status_bar_text.emit("")
        self.set_status_bar_percent.emit(100)

        self.result_ready.emit()
        QtCore.QThread.currentThread().quit()

class table_model(QtCore.QAbstractTableModel):
    def __init__(self, p_parent:QtCore.QObject):
        self.parent = p_parent
        super().__init__(p_parent)
        self.raw_list = list()
        self.update_data(data_provider.load_existing_from_db())
        self.app_id_to_row = dict()

    def get_index_from_app_id(self, p_app_id: int, p_col: int) -> QtCore.QModelIndex:
        row = self.app_id_to_row[p_app_id]
        return self.createIndex(row, p_col)

    def rowCount(self, p_index: QtCore.QModelIndex):
        return len(self.raw_list)

    def columnCount(self, p_index: QtCore.QModelIndex):
        # Enabled, Preview(Capsule), appID, name, last updated, last played
        return 6

    def flags(self, p_index: QtCore.QModelIndex):
        column = p_index.column()

        flags = super().flags(p_index)
        if column == 0:
            flags |= QtCore.Qt.ItemFlag.ItemIsUserCheckable
            return flags
        else:
            return flags

    def setData(self,
            p_index: QtCore.QModelIndex,
            p_value,
            p_role: QtCore.Qt.ItemDataRole) -> bool:
        item = self.raw_list[p_index.row()]
        if (p_role == QtCore.Qt.ItemDataRole.CheckStateRole and
            p_index.column() == 0):
                data_provider.set_enable_app_id(
                    [item['app_id']],
                    QtCore.Qt.CheckState(p_value) == QtCore.Qt.CheckState.Checked)
                return True
        elif (p_role == QtCore.Qt.ItemDataRole.DecorationRole and p_index.column() == 1):
            self.dataChanged.emit(p_index, p_index, [QtCore.Qt.ItemDataRole.DecorationRole])
            return True
        else:
            return super().setData(p_index, p_value, p_role)


    def data(self,
            p_index: QtCore.QModelIndex,
            p_role: QtCore.Qt.ItemDataRole):

        item = self.raw_list[p_index.row()]
        column = p_index.column()

        if p_role == QtCore.Qt.ItemDataRole.CheckStateRole:
            if column == 0:
                if data_provider.should_download_appid(item['app_id']):
                    return QtCore.Qt.CheckState.Checked
                else:
                    return QtCore.Qt.CheckState.Unchecked
        if p_role == QtCore.Qt.ItemDataRole.DecorationRole:
            if column == 1:
                if game_header_availible(item['app_id']) == 2:
                    header_name = f"{item['app_id']}.jpg"
                    cached_image_location = os.path.join(core.s_cache_header_dir, header_name)
                    return QtGui.QIcon(cached_image_location)
            else:
                return None

        if p_role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None

        self.app_id_to_row[item['app_id']] = p_index.row()

        if column == 0:
            pass
        elif column == 1:
            # Return 0 if not checked yet
            # Retrun 1 if 404
            # Retrun 2 if found
            availibility = game_header_availible(item['app_id'])
            if availibility == 0:
                return "Loading"
            elif availibility == 1:
                return "N/A"
            elif availibility == 2:
                return None
        elif column == 2:
            return item['app_id']
        elif column == 3:
            return item['name']
        elif column == 4:
            if item['last_checked_time'] is None:
                return 'N/A'
            else:
                return str(item['last_checked_time'])
        elif column == 5:
            if item['last_played'] is None:
                return 'N/A'
            else:
                return str(item['last_played'])
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
                return 'Header'
            elif p_section == 2:
                return 'App ID'
            elif p_section == 3:
                return 'Name'
            elif p_section == 4:
                return 'Last Updated'
            elif p_section == 5:
                return 'Last Played'
            else:
                assert(False)
        else:
            return super().headerData(p_section, p_orient, p_role)

    # Requires: [{'app_id': "value", 'name': "value"}]
    def update_data(self, p_list: list):
        self.beginResetModel()
        self.raw_list = p_list
        self.endResetModel()

    def get_app_id_list(self) -> list :
        return sorted([item['app_id'] for item in self.raw_list])

class table_sort_filter_proxy(QtCore.QSortFilterProxyModel):
    def __init__(self,
                 p_parent:QtCore.QObject,
                 p_source_model: table_model):
        super().__init__(p_parent)
        self.setSourceModel(p_source_model)
        self.filter = ""

    def filterAcceptsRow(self, p_source_row: int, p_source_parent: QtCore.QModelIndex) -> bool:
        app_id_index = \
            self.sourceModel().index(p_source_row, 2, p_source_parent)
        name_index = \
            self.sourceModel().index(p_source_row, 3, p_source_parent)
        app_id = \
            self.sourceModel().data(
                app_id_index, QtCore.Qt.ItemDataRole.DisplayRole)
        name = \
            self.sourceModel().data(
                name_index, QtCore.Qt.ItemDataRole.DisplayRole)

        return (self.filter in str(app_id)) or (self.filter.lower() in name.lower())

    @QtCore.Slot(str)
    def set_filter_text(self, p_filter: str):
        self.filter = p_filter
        self.invalidateFilter()

def get_game_info_dialog(p_model: table_sort_filter_proxy, p_index: QtCore.QModelIndex):
    app_id_index = p_model.index(p_index.row(), 2)
    app_id = \
        p_model.data(app_id_index, QtCore.Qt.ItemDataRole.DisplayRole)

    game_name_index = p_model.index(p_index.row(), 3)
    game_name = p_model.data(
        game_name_index,
        QtCore.Qt.ItemDataRole.DisplayRole)

    dialog = game_info_dialog(app_id, game_name)
    result:QW.QDialog.DialogCode = dialog.exec()

class enable_all_action(QtGui.QAction):
    def __init__(self):
        super().__init__("Enable All")
        self.triggered.connect(self.execute)

    @QtCore.Slot(bool)
    def execute(self, p_b: bool):
        data_provider.set_enable_all_app_id()

class disable_all_action(QtGui.QAction):
    def __init__(self, p_table_model: table_sort_filter_proxy):
        super().__init__("Disable All")
        self.table_model = p_table_model
        self.triggered.connect(self.execute)

    @QtCore.Slot(bool)
    def execute(self, p_b: bool):
        exclude_list = list()
        for i in range(self.table_model.rowCount()):
            index = self.table_model.index(i, 2)
            data = self.table_model.data(index)
            exclude_list.append(data)
        data_provider.set_enable_app_id(exclude_list, False)

class view_files_action(QtGui.QAction):
    def __init__(self,
                p_model: table_sort_filter_proxy,
                p_index: QtCore.QModelIndex):
        super().__init__("View Save Files")

        self.model = p_model
        self.index = p_index
        self.triggered.connect(self.execute)

    @QtCore.Slot(bool)
    def execute(self, p_b: bool):
        get_game_info_dialog(self.model, self.index)

class open_saves_directory_action(QtGui.QAction):
    def __init__(self,
                p_model: table_sort_filter_proxy,
                p_index: QtCore.QModelIndex):
        super().__init__("Open Saves Directory")

        self.model = p_model
        self.index = p_index
        self.triggered.connect(self.execute)

    @QtCore.Slot(bool)
    def execute(self, p_b: bool):
        app_id_index = self.model.index(self.index.row(), 2)
        app_id = \
            self.model.data(app_id_index, QtCore.Qt.ItemDataRole.DisplayRole)

        save_dir = data_provider.get_save_dir(app_id)
        if (not os.path.isdir(save_dir)):
            # TODO: Handle This
            print(f"Error {save_dir} not exit")
            return

        webbrowser.open("file:///" + str(save_dir))

class table_csm(QW.QMenu):
    def __init__(self,
                p_parent: QW.QWidget,
                p_model: table_sort_filter_proxy,
                p_index: QtCore.QModelIndex):
        super().__init__(p_parent)

        self.game_info_action = view_files_action(p_model, p_index)
        self.addAction(self.game_info_action)

        self.open_saves_directory_action = open_saves_directory_action(p_model, p_index)
        self.addAction(self.open_saves_directory_action)

        self.enable_all_action = enable_all_action()
        self.addAction(self.enable_all_action)
        self.disable_all_action = disable_all_action(p_model)
        self.addAction(self.disable_all_action)

class table_view(QW.QTableView):
    def __init__(self, p_parent:QtCore.QObject):
        super().__init__(p_parent)
        self.setMinimumSize(800, 500)

        self.verticalHeader().hide()

        self.setSelectionBehavior(
            QW.QAbstractItemView.SelectionBehavior.SelectRows)

        self.setSortingEnabled(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.verticalHeader().setSectionResizeMode(QW.QHeaderView.ResizeMode.Fixed)
        self.verticalHeader().setDefaultSectionSize(43)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_csm_requested)

        self.doubleClicked.connect(self.on_double_clicked)
        self.setIconSize(QtCore.QSize(92, 43))

    @QtCore.Slot(QtCore.QModelIndex)
    def on_double_clicked(self, p_index: QtCore.QModelIndex):
        get_game_info_dialog(self.model(), p_index)

    @QtCore.Slot(QtCore.QPoint)
    def on_csm_requested(self, p_point: QtCore.QPoint):
        index = self.indexAt(p_point)

        menu = table_csm(self, self.model(), index)
        menu.popup(self.viewport().mapToGlobal(p_point))

    def set_header_stretch(self, p_section_size:int):
        for i in range(p_section_size - 1):
            self.horizontalHeader().setSectionResizeMode(
                i,
                QW.QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(
            p_section_size - 1,
            QW.QHeaderView.ResizeMode.Stretch)


class table_widget(QW.QWidget):
    def __init__(self, p_parent: QtCore.QObject, p_status_bar: status_bar):
        super().__init__(p_parent)
        self.status_bar = p_status_bar

        self.table_view = table_view(self)
        self.table_model = table_model(self)
        self.sort_filter_model = table_sort_filter_proxy(self, self.table_model)

        self.table_view.setModel(self.sort_filter_model)

        self.table_view.set_header_stretch(self.table_model.columnCount(None))
        self.sort_filter_model.sort(2, QtCore.Qt.SortOrder.AscendingOrder)

        self.create_search_box()

        self.v_layout = QW.QVBoxLayout(self)
        self.v_layout.addWidget(self.search_box)
        self.v_layout.addWidget(self.table_view)

        self.start_download_header()

    def create_search_box(self):
        self.search_box = QW.QLineEdit()
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setPlaceholderText("Search App ID / Name")
        self.search_box.textChanged.connect(self.sort_filter_model.set_filter_text)

    def on_main_window_closed(self):
        self.header_download_controller.stop()

    def start_download_header(self):
        self.header_downloader = \
            game_header_downloader(self.table_model.get_app_id_list())
        self.header_download_controller = thread_controller.thread_controller(self.header_downloader)

        self.header_download_controller.job_notified.connect(self.on_header_download_notify)

        self.header_download_controller.start()

    @QtCore.Slot(int)
    def on_header_download_notify(self, p_int: int):
        index = self.table_model.get_index_from_app_id(p_int, 1)
        self.table_model.setData(index, None, QtCore.Qt.ItemDataRole.DecorationRole)

    @QtCore.Slot(list)
    def refresh(self):
        # Refresh
        self.refresher = \
            table_refresher(self)
        self.refresher_controller = thread_controller.thread_controller(self.refresher, self.status_bar)
        self.refresher_controller.job_finished.connect(self.on_refresh_complete)
        self.refresher_controller.start()

    @QtCore.Slot(int)
    def on_row_change(self, p_int):
        pass

    @QtCore.Slot()
    def on_refresh_complete(self):
        logger.debug("(refresher) Refresh complete")
        self.start_download_header()