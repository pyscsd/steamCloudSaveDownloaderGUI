from .steamCloudSaveDownloader.steamCloudSaveDownloader.auth import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader.config import config as config_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader.db import db as db_c
from .steamCloudSaveDownloader.steamCloudSaveDownloader.web import web
from .core import core
import copy
import pickle # TODO: Remove
import os # TODO: Remove

# This file is a singleton

config_client = config_c(core.s_config_file)
config = config_client.get_conf()
exclude_set = set(config['Target']['list'])
db = db_c(core.s_config_dir, config['Rotation']['rotation'])

# TODO: Uncomment when mock finished
# TODO: Refresh session whenever do it
'''
self.auth = auth(core.s_config_dir, '')
self.auth.refresh_session()
self.web = web(self.auth.get_session_path(), self.config['Danger Zone']['wait_interval'])
'''

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

def load_existing_from_db():
    id_and_names = db.get_stored_game_names([])
    return [{'app_id': app_id, 'name': name} for app_id, name in id_and_names]


def load_from_pkl():
    with open(os.path.join(core.s_config_dir, 'game_list.pkl'), 'rb') as f:
        game_list = pickle.load(f)
    return game_list

def get_game_list_from_web():
    data = load_from_pkl()
    return data
    #self.web.get_list()
    '''
    with open(os.path.join(core.s_config_dir, 'game_list.pkl'), 'wb') as f:
        pickle.dump(self.web.get_list(), f)
    '''

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