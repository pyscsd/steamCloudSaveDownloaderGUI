from enum import Enum
from PySide6 import QtWidgets as QW
from PySide6 import QtCore, QtGui

from .steamCloudSaveDownloader.steamCloudSaveDownloader.downloader import downloader as core_downloader
from .steamCloudSaveDownloader.steamCloudSaveDownloader.downloader import callback_method_e
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger

from . import data_provider
from . import status_bar
from . import thread_controller

class mode_e(Enum):
    download_all = 1
    download_local_outdated = 2

class interupt_exception(Exception):
    pass

# TODO: Check lock before download

class save_downloader(QtCore.QObject):
    job_finished = QtCore.Signal()
    job_notified = QtCore.Signal(int)

    @staticmethod
    def can_download() -> bool:
        return not core_downloader.has_lock_file(data_provider.config)

    def __init__(self, p_mode: mode_e, p_status_bar: status_bar.status_bar | None):
        super().__init__()
        self.status_bar = p_status_bar
        self.mode = p_mode

    def setup(self) -> bool:
        if not self.can_download():
            return False

        self.downloader = _save_downloader(self.mode)
        self.downloader_controller = \
            thread_controller.thread_controller(self.downloader, self.status_bar)
        self.downloader_controller.job_finished.connect(self.download_complete)
        self.downloader_controller.job_notified.connect(self.app_id_updated)

        return True

    def stop(self):
        if hasattr(self, "downloader_controller"):
            self.downloader_controller.stop()

    def download_complete(self):
        self.job_finished.emit()

    def app_id_updated(self, p_value: int):
        self.job_notified.emit(p_value)

    def one_shot_download(self):
        if not self.setup():
            return
        self.downloader_controller.start()

    def periodic_download(self):
        if not self.setup():
            return
        # TODO

class _save_downloader(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)
    set_status_bar_text = QtCore.Signal(str)
    set_status_bar_percent = QtCore.Signal(int)
    def __init__(self, p_mode: mode_e):
        super().__init__()
        self.mode = p_mode

    def download_games(self, p_target_game_list: list):
        if len(p_target_game_list) == 0:
            return

        progress_step = 100 / len(p_target_game_list)
        current_progress = 0
        count = 1
        for game in p_target_game_list:
            if self.check_interrupt():
                break
            logger.info(f"Downlading {game['name']}")
            self.set_status_bar_text.emit(f"Downlading {game['name']} ({count} / {len(p_target_game_list)})")
            self.set_status_bar_percent.emit(current_progress)

            self.downloader.download_game(game)
            self.notification.emit(game['app_id'])

            current_progress += progress_step
            count += 1

            # TODO: Update table


    def download_local_outdated(self):

        # TODO: Handle timezone issue
        last_played = data_provider.get_games_last_played_time_locally()
        db_info = data_provider.get_last_checked_time_from_db()

        target_game_list = list()
        for game in self.downloader.game_list:
            app_id = game['app_id']
            if app_id not in db_info:
                target_game_list.append(game)
                continue

            if app_id not in last_played:
                target_game_list.append(game)
                continue

            last_checked_time = db_info[app_id]
            last_played_time = last_played[app_id]

            if last_checked_time < last_played_time:
                target_game_list.append(game)
            else:
                logger.debug(f"{game['app_id']} skipped. DB Time: {last_checked_time}. Last played time: {last_played_time}")

        self.download_games(target_game_list)

    def download_all(self):
        target_game_list = \
            [game for game in self.downloader.game_list if data_provider.should_download_appid(game['app_id'])]

        logger.debug(f"Download All Game list count: {len(target_game_list)}")

        self.download_games(target_game_list)


    def check_interrupt(self):
        interrupt = QtCore.QThread.currentThread().isInterruptionRequested()
        if interrupt:
            logger.debug("(save_downloader) interrupt recieved")
        return interrupt

    def downloading_game_file_callback(self, p_game_name: str, p_file_name: str):
        if self.check_interrupt():
            logger.debug("Interrupt in file download callback")
            raise interupt_exception
        self.set_status_bar_text.emit(f"Downlading {p_game_name}: {p_file_name}")

    @QtCore.Slot()
    def do_job(self):
        self.set_status_bar_text.emit("Initializing...")
        self.set_status_bar_percent.emit(0)

        self.downloader = core_downloader(data_provider.config)
        self.downloader.set_callback(
            self.downloading_game_file_callback,
            callback_method_e.download_game_file)

        logger.debug("(save_downloader) do_job")

        try:
            if (self.mode == mode_e.download_all):
                self.download_all()
            elif (self.mode == mode_e.download_local_outdated):
                self.download_local_outdated()
        except interupt_exception:
            pass

        self.set_status_bar_percent.emit(100)
        self.result_ready.emit()

        del self.downloader
        QtCore.QThread.currentThread().quit()