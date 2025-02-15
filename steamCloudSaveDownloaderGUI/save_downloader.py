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

    def download_all(self):
        target_game_list = [game for game in self.downloader.game_list if data_provider.should_download_appid(game['app_id'])]

        progress_step = 100 / len(target_game_list)
        logger.debug(f"Game list count: {len(target_game_list)}")

        current_progress = 0
        count = 1
        for game in self.downloader.game_list:
            if self.check_interrupt():
                break
            logger.info(f"Downlading {game['name']}")
            self.set_status_bar_text.emit(f"Downlading {game['name']} ({count} / {len(target_game_list)})")
            self.set_status_bar_percent.emit(current_progress)

            self.downloader.download_game(game)

            current_progress += progress_step
            count += 1


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
            pass
        self.set_status_bar_percent.emit(100)
        self.result_ready.emit()
        QtCore.QThread.currentThread().quit()

        # TODO: Check interrupt
        # TODO: Deeper callback