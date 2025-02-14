from .steamCloudSaveDownloader.steamCloudSaveDownloader.config import config as config_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader.db import db as db_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader import downloader
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger, set_level
from .core import core
import copy
from datetime import datetime
import os
import vdf

# This file is a singleton

config_client = config_c(core.s_config_file)
config = config_client.get_conf()
exclude_set = set(config['Target']['list'])

def reload_config():
    global config_client, config, exclude_set

    config_client = config_c(core.s_config_file)
    config = config_client.get_conf()
    exclude_set = set(config['Target']['list'])

def commit(p_config=None):
    if p_config is None:
        config_client.export_to_file(config, core.s_config_file)
    else:
        config_client.export_to_file(p_config, core.s_config_file)
    reload_config()
    set_level(config['Log']['log_level'])

    logger.debug(f'Options: {config}')

def get_games_last_played_time_locally() -> dict:
    global account_id
    account_id = downloader.get_account_id(config)
    logger.debug(f"Account_id: {account_id}")

    vdf_location = os.path.join(core.s_steam_location, "userdata", str(account_id), 'config', "localconfig.vdf")
    if not os.path.isfile(vdf_location):
        return
    local_vdf = vdf.load(open(vdf_location, encoding='utf-8'))

    played_time = {}

    for key, value in local_vdf['UserLocalConfigStore']['Software']['valve']['Steam']['apps'].items():
        if 'LastPlayed' not in value:
            continue
        played_time[int(key)] = datetime.fromtimestamp(int(value['LastPlayed']))
    return played_time


def load_existing_from_db():
    global account_id
    if not core.has_session():
        return []
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    info = db.get_all_stored_game_infos()

    last_played = get_games_last_played_time_locally()

    data = list()

    for app_id, name, last_checked_time in info:
        if app_id in last_played:
            data.append({'app_id': app_id, 'name': name, 'last_checked_time': last_checked_time, 'last_played': last_played[app_id]})
        else:
            data.append({'app_id': app_id, 'name': name, 'last_checked_time': last_checked_time, 'last_played': None})
    return data

def load_from_db_and_web():
    db_list = load_existing_from_db()
    existing_app_id_dict = {item['app_id'] for item in db_list}
    web_list = downloader.get_game_list_and_update(config)

    new_list = copy.copy(db_list)

    last_played = get_games_last_played_time_locally()

    for item in web_list:
        if item['app_id'] not in existing_app_id_dict:
            logger.debug(f'app_id {item["app_id"]} not found in DB')
            new_list.append(
                {
                    'app_id': item['app_id'],
                    'name': item['name'],
                    'last_checked_time': None,
                    'last_played': last_played[item['app_id']] if item['app_id'] in last_played else None
                })
    return new_list


def get_files_from_app_id(p_app_id: int):
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    # file_id, filename, location in files_info:
    return db.get_files_info_by_appid(p_app_id)

def get_file_version_by_file_id(p_file_id: int):
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    return db.get_file_version_by_file_id(p_file_id)

def should_download_appid(app_id: int) -> bool:
    return app_id not in exclude_set

# Return True if modified, False otherwise
def set_enable_app_id(app_id: int, enable: bool) -> bool:
    if app_id in exclude_set:
        if enable:
            exclude_set.remove(app_id)
            config['Target']['list'] = list(exclude_set)
        else:
            return False
    else:
        if enable:
            return False
        else:
            config['Target']['list'].append(app_id)

    commit()
    return True

def get_save_dir(app_id: int) -> os.path:
    return os.path.join(config['General']["save_dir"], str(app_id))

def get_config_copy() -> dict:
    return copy.copy(config)