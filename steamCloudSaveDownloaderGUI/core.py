import os
import sys
import pathlib
import platform
from .steamCloudSaveDownloader.steamCloudSaveDownloader import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader import config
from .steamCloudSaveDownloader.steamCloudSaveDownloader import db
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger

def get_windows_steam_install_location():
    import winreg
    try:
        uninstall_info = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam")
    except FileNotFoundError:
        logger.info("Steam Win Reg Key Not found")
        return ""
    try:
        location = winreg.QueryValueEx(uninstall_info, "UninstallString")
    except FileNotFoundError:
        logger.info("UninstallString Not found")
        return ""
    location = location[0]
    location = pathlib.Path(location)
    location = os.path.join(*location.parts[0:-1])
    return location

def get_steam_install_location():
    if platform.system() == 'Windows':
        return get_windows_steam_install_location()
    return ""

class core:
    def __init__(self):
        pass

    s_initial_config_reload_required = False
    s_config_dir = os.path.join(pathlib.Path.home(), "scsd")
    s_config_file = os.path.join(s_config_dir, "scsd.conf")
    s_db_file = os.path.join(s_config_dir, "scsd.sqlite3")
    s_log_file = os.path.join(s_config_dir, "scsd.log")
    s_cache_dir = os.path.join(s_config_dir, ".cache")
    s_account_id_file = os.path.join(s_config_dir, "account_id")
    s_cache_header_dir = os.path.join(s_cache_dir, "header")
    s_cache_translation_dir = os.path.join(s_cache_dir, "translation")
    s_default_save_dir = os.path.join(pathlib.Path.home(), "scsd", "saves")
    s_session_file = os.path.join(s_config_dir, auth.auth.s_session_filename)
    s_steam_location = get_steam_install_location()

    @staticmethod
    def init():
        logger.debug("Core Init")
        if not os.path.isdir(core.s_config_dir):
            logger.debug(f"Creating {core.s_config_dir}")
            os.mkdir(core.s_config_dir)
        if not os.path.isdir(core.s_default_save_dir):
            logger.debug(f"Creating {core.s_default_save_dir}")
            os.mkdir(core.s_default_save_dir)
        if not os.path.isdir(core.s_cache_dir):
            logger.debug(f"Creating {core.s_cache_dir}")
            os.mkdir(core.s_cache_dir)
            # TODO: .cache, hide attribute in windows
        if not os.path.isdir(core.s_cache_header_dir):
            logger.debug(f"Creating {core.s_cache_header_dir}")
            os.mkdir(core.s_cache_header_dir)
        if not os.path.isdir(core.s_cache_translation_dir):
            logger.debug(f"Creating {core.s_cache_translation_dir}")
            os.mkdir(core.s_cache_translation_dir)
        if not os.path.isfile(core.s_db_file):
            logger.debug(f"Creating db")
            db_ = db.db(core.s_config_dir, 10)
            del db_

        if not os.path.isfile(core.s_config_file):
            logger.debug(f"Creating initial config")
            initial_config = {
                'General': {
                    "save_dir": core.s_default_save_dir,
                    "config_dir": core.s_config_dir
                },
                'Target': {
                    "mode": "exclude"
                }
            }
            config.config.export_to_file(initial_config, core.s_config_file)
            core.s_initial_config_reload_required = True

    @staticmethod
    def has_session() -> bool:
        return os.path.isfile(core.s_session_file)

    @staticmethod
    def set_start_on_startup(p_enable: bool):
        if platform.system() == 'Windows':
            from win32com.client import Dispatch as win_dispatch


            logger.debug(f"Windows env")
            if hasattr(sys, '_MEIPASS'):
                app_path = sys.executable
                logger.debug(f"App path: {app_path}")
            else:
                logger.debug(f"Auto startup not supported in script mode")
                return

            exe_name = os.path.basename(app_path)
            exe_stem = pathlib.Path(exe_name).stem
            logger.debug(f"Executable name: {exe_name}")
            logger.debug(f"Executable stem: {exe_stem}")

            app_data = os.getenv('APPDATA')
            startup_shortcut = os.path.join(app_data, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', f"{exe_stem}.lnk")

            logger.debug(f"Startup_location: {startup_shortcut}")

            if p_enable:
                if os.path.isfile(startup_shortcut):
                    logger.debug(f"Link exist. Skipped")
                    return
                shell = win_dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(startup_shortcut)
                shortcut.Targetpath = str(pathlib.Path(app_path))
                shortcut.Arguments = '--minimize'
                shortcut.save()
            else:
                if os.path.isfile(startup_shortcut):
                    os.remove(startup_shortcut)
                    logger.debug(f"Remove startup link")
