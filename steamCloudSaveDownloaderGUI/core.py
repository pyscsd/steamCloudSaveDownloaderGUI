import pathlib
import os
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth

class core:
    def __init__(self):
        pass
    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
    s_session_file = os.path.join(s_config_dir, auth.auth.s_session_filename)

    @staticmethod
    def init():
        if not os.path.isdir(core.s_config_dir):
            os.mkdir(core.s_config_dir)