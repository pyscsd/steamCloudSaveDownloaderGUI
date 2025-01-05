import pathlib
import os
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader import config
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger

class core:
    def __init__(self):
        pass

    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
    s_log_file = os.path.join(s_config_dir, "scsd.log")
    s_cache_dir = os.path.join(s_config_dir, ".cache")
    s_cache_header_dir = os.path.join(s_cache_dir, "header")
    s_default_save_dir = os.path.join(pathlib.Path.home(), "scsd", "saves")
    s_session_file = os.path.join(s_config_dir, auth.auth.s_session_filename)

    @staticmethod
    def init():
        if not os.path.isdir(core.s_config_dir):
            logger.debug(f"Creating {core.s_config_dir}")
            os.mkdir(core.s_config_dir)
        if not os.path.isdir(core.s_default_save_dir):
            logger.debug(f"Creating {core.s_default_save_dir}")
            os.mkdir(core.s_default_save_dir)
        if not os.path.isdir(core.s_cache_dir):
            logger.debug(f"Creating {core.s_cache_dir}")
            os.mkdir(core.s_cache_dir)
        if not os.path.isdir(core.s_cache_header_dir):
            logger.debug(f"Creating {core.s_cache_header_dir}")
            os.mkdir(core.s_cache_header_dir)
            # TODO: .cache, hide attribute in windows
        if not os.path.isfile(core.s_config_file):
            logger.debug(f"Creating initial config")
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