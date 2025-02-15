from enum import Enum
from PySide6 import QtWidgets as QW
from PySide6 import QtCore, QtGui

from .steamCloudSaveDownloader.steamCloudSaveDownloader.downloader import downloader as core_downloader
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger

from . import data_provider

class mode_e(Enum):
    download_all = 1
    download_local_outdated = 2

class save_downloader(QtCore.QObject):
    result_ready = QtCore.Signal()
    notification = QtCore.Signal(int)
    set_status_bar_text = QtCore.Signal(str)
    set_status_bar_percent = QtCore.Signal(int)
    def __init__(self, p_mode: mode_e):
        super().__init__()
        self.mode = p_mode

    def download_games(self, p_target_game_list: list):
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

    @QtCore.Slot()
    def do_job(self):
        self.set_status_bar_text.emit("Initializing...")
        self.set_status_bar_percent.emit(0)
        self.downloader = core_downloader(data_provider.config)
        logger.debug("(save_downloader) do_job")
        if (self.mode == mode_e.download_all):
            self.download_all()
        elif (self.mode == mode_e.download_local_outdated):
            self.download_local_outdated()
        self.set_status_bar_percent.emit(100)
        self.result_ready.emit()

        del self.downloader
        QtCore.QThread.currentThread().quit()

        # TODO: Check interrupt
        # TODO: Deeper callback