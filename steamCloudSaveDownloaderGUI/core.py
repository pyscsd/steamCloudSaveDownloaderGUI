import pathlib
import os
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader import config

class core:
    def __init__(self):
        pass
    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
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
                }
            }
            config.config.export_to_file(initial_config, core.s_config_file)