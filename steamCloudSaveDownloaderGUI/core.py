import pathlib
import os
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader import config

class core:
    def __init__(self):
        pass
    # TODO: COnfig, save, .cache,
    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
    s_cache_dir = os.path.join(s_config_dir, ".cache")
    s_default_save_dir = os.path.join(pathlib.Path.home(), "scsd", "saves")
    s_session_file = os.path.join(s_config_dir, auth.auth.s_session_filename)

    @staticmethod
    def init():
        if not os.path.isdir(core.s_config_dir):
            os.mkdir(core.s_config_dir)
        if not os.path.isdir(core.s_default_save_dir):
            os.mkdir(core.s_default_save_dir)
        if not os.path.isfile(core.s_config_file):
            initial_config = {
                'General': {
                    "save_dir": core.s_default_save_dir
                },
                'Rotation': {
                    "rotation": config.Defaults['Rotation']['rotation'][1]
                }
            }
            config.config.export_to_file(initial_config, core.s_config_file)

    @staticmethod
    def has_session() -> bool:
        return os.path.isfile(core.s_session_file)