from .steamCloudSaveDownloader.steamCloudSaveDownloader.config import config as config_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader.db import db as db_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader import downloader
from .steamCloudSaveDownloader.steamCloudSaveDownloader.logger import logger, set_level
from .core import core
import copy
import datetime
from dateutil import tz
import os
from PySide6.QtCore import QLocale
import json
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
        return {}
    local_vdf = vdf.load(open(vdf_location, encoding='utf-8'))

    played_time = {}

    try:
        items = local_vdf['UserLocalConfigStore']['Software']['valve']['Steam']['apps'].items()
    except:
        try:
            # Might be lower case
            items = local_vdf['UserLocalConfigStore']['Software']['Valve']['Steam']['apps'].items()
        except:
            return {}

    for key, value in items:
        if 'LastPlayed' not in value:
            continue
        played_time[int(key)] = \
            datetime.datetime.fromtimestamp(int(value['LastPlayed']))
    return played_time

def get_last_checked_time_from_db():
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    infos = db.get_all_stored_game_infos()
    info_dict = {info[0]: info[2] for info in infos}
    return info_dict

# DB Time zone is PST(?)
# Last Checked is UTC(?)

g_local_timezone = \
    datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
def _set_local_time_as_local_timezone(p_datetime: datetime.datetime):
    global g_local_timezone

    if p_datetime.tzinfo != None:
        return
    dt = p_datetime.replace(tzinfo=datetime.timezone.utc)
    dt = dt.astimezone(g_local_timezone)
    dt = dt.replace(tzinfo=None)
    return dt

g_server_timezone = tz.gettz('America/Los_Angeles')
def _set_server_time_as_local_timezone(p_datetime: datetime.datetime):
    global g_server_timezone, g_local_timezone

    if p_datetime.tzinfo != None:
        return
    dt = p_datetime.replace(tzinfo=g_server_timezone)
    dt = dt.astimezone(g_local_timezone)
    dt = dt.replace(tzinfo=None)
    return dt

def get_language_code():
    language_code = config['GUI']['language']
    if language_code == 'system':
        return QLocale.system().name()
    else:
        return language_code

def get_cached_game_list_translation():
    return os.path.join(core.s_cache_translation_dir, f"{get_language_code()}.json")

def read_cached_game_list_translation():
    file = get_cached_game_list_translation()
    if not os.path.isfile(file):
        return {}

    with open(file, 'r') as f:
        return json.load(f)

def write_cached_game_list_translation(p_translation: list):
    if p_translation is None:
        return
    file = get_cached_game_list_translation()

    output = {dict_['app_id']: dict_['name'] for dict_ in p_translation}

    with open(file, 'w') as f:
        json.dump(output, f)

def load_existing_from_db():
    global account_id
    if not core.has_session():
        return []
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    infos = db.get_all_stored_game_infos()

    last_played = get_games_last_played_time_locally()

    data = list()

    translated_game_dict = read_cached_game_list_translation()

    for app_id, default_name, last_checked_time in infos:
        if str(app_id) in translated_game_dict:
            name = translated_game_dict[str(app_id)]
        else:
            name = default_name
        if app_id in last_played:
            data.append({'app_id': app_id, 'name': name, 'last_checked_time': last_checked_time, 'last_played': last_played[app_id]})
        else:
            data.append({'app_id': app_id, 'name': name, 'last_checked_time': last_checked_time, 'last_played': None})

    for item in data:
        item['last_checked_time'] = _set_local_time_as_local_timezone(item['last_checked_time'])

    return data

def load_from_db_and_web():
    db_list = load_existing_from_db()
    existing_app_id_dict = {item['app_id'] for item in db_list}
    web_list = downloader.get_game_list_and_update(config)

    new_list = copy.copy(db_list)

    last_played = get_games_last_played_time_locally()


    write_cached_game_list_translation(
        downloader.get_game_list(config, get_language_code()))
    translated_game_dict = read_cached_game_list_translation()

    for item in web_list:
        if item['app_id'] in existing_app_id_dict:
            continue
        logger.debug(f'app_id {item["app_id"]} not found in DB')
        name = item['name']
        if str(item['app_id']) in translated_game_dict:
            name = translated_game_dict[item['app_id']]
        new_list.append({
                'app_id': item['app_id'],
                'name': name,
                'last_checked_time': None,
                'last_played': last_played[item['app_id']] if item['app_id'] in last_played else None
            })
    return new_list

def get_game_info_from_app_id(p_app_id: int):
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    # game name, dir name, last_checked_time
    game_info = db.get_game_info_by_appid(p_app_id)
    local_time_game_info = list()
    for item in game_info:
        local_time_game_info.append(
            (item[0], item[1], _set_local_time_as_local_timezone(item[2])))
    return local_time_game_info

def get_files_from_app_id(p_app_id: int):
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    # file_id, filename, location in files_info:
    return db.get_files_info_by_appid(p_app_id)

def get_file_version_by_file_id(p_file_id: int):
    db = db_c(core.s_config_dir, config['Rotation']['rotation'])
    version_info = db.get_file_version_by_file_id(p_file_id)
    return [(_set_server_time_as_local_timezone(date), num) for date, num in version_info]

def should_download_appid(app_id: int) -> bool:
    global exclude_set
    return app_id not in exclude_set

def set_enable_all_app_id():
    global exclude_set

    exclude_set.clear()
    config['Target']['list'] = list(exclude_set)
    commit()

def set_enable_app_id(p_app_id_list: list, p_enable: bool):
    global exclude_set

    for app_id in p_app_id_list:
        if app_id in exclude_set:
            if p_enable:
                exclude_set.remove(app_id)
            else:
                continue
        else:
            if p_enable:
                continue
            else:
                exclude_set.add(app_id)
    config['Target']['list'] = list(exclude_set)
    commit()

def get_save_dir(app_id: int) -> os.path:
    return os.path.join(config['General']["save_dir"], str(app_id))

def get_config_copy() -> dict:
    return copy.deepcopy(config)
