import pathlib
import os
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader import config
from .steamCloudSaveDownloader.steamCloudSaveDownloader import db
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger

class core:
    def __init__(self):
        pass

    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
    s_db_file = os.path.join(s_config_dir, "scsd.sqlite3")
    s_log_file = os.path.join(s_config_dir, "scsd.log")
    s_cache_dir = os.path.join(s_config_dir, ".cache")
    s_cache_header_dir = os.path.join(s_cache_dir, "header")
    s_default_save_dir = os.path.join(pathlib.Path.home(), "scsd", "saves")
    s_session_file = os.path.join(s_config_dir, auth.auth.s_session_filename)

    @staticmethod
    def init():
        logger.info("Core Init")
        if not os.path.isdir(core.s_config_dir):
            logger.info(f"Creating {core.s_config_dir}")
            os.mkdir(core.s_config_dir)
        if not os.path.isdir(core.s_default_save_dir):
            logger.info(f"Creating {core.s_default_save_dir}")
            os.mkdir(core.s_default_save_dir)
        if not os.path.isdir(core.s_cache_dir):
            logger.info(f"Creating {core.s_cache_dir}")
            os.mkdir(core.s_cache_dir)
        if not os.path.isdir(core.s_cache_header_dir):
            logger.info(f"Creating {core.s_cache_header_dir}")
            os.mkdir(core.s_cache_header_dir)
            # TODO: .cache, hide attribute in windows
        if not os.path.isfile(core.s_db_file):
            logger.info(f"Creating db")
            db_ = db.db(core.s_config_dir, 10)
            del db_

        if not os.path.isfile(core.s_config_file):
            logger.info(f"Creating initial config")
            initial_config = {
                'General': {
                    "save_dir": core.s_default_save_dir,
                    "config_dir": core.s_config_dir
                },
                'Rotation': {
                    "rotation": config.Defaults['Rotation']['rotation'][1]
                }
            }
            config.config.export_to_file(initial_config, core.s_config_file)

    @staticmethod
    def has_session() -> bool:
        return os.path.isfile(core.s_session_file)