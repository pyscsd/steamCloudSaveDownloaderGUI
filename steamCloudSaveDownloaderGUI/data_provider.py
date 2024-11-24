from .steamCloudSaveDownloader.steamCloudSaveDownloader.auth import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader.config import config
from .steamCloudSaveDownloader.steamCloudSaveDownloader.db import db
from .steamCloudSaveDownloader.steamCloudSaveDownloader.web import web
from .core import core
import pickle # TODO: Remove
import os # TODO: Remove

class data_provider:
    def __init__(self) -> None:
        self.reload_config()
        self.db = db(core.s_config_dir, self.config['Rotation']['rotation'])
        # TODO: Uncomment when mock finished
        '''
        self.auth = auth(core.s_config_dir, '')
        self.auth.refresh_session()
        self.web = web(self.auth.get_session_path(), self.config['Danger Zone']['wait_interval'])
        '''

    def reload_config(self):
        self.config_client = config(core.s_config_file)
        self.config = self.config_client.get_conf()
        self.exclude_set = set(self.config['Target']['list'])

    def load_existing_from_db(self):
        id_and_names = self.db.get_stored_game_names([])
        return [{'app_id': app_id, 'name': name} for app_id, name in id_and_names]

    def get_game_list_from_web(self):
        data = self.load_from_pkl()
        return data
        #self.web.get_list()
        '''
        with open(os.path.join(core.s_config_dir, 'game_list.pkl'), 'wb') as f:
            pickle.dump(self.web.get_list(), f)
        '''

    def load_from_pkl(self):
        with open(os.path.join(core.s_config_dir, 'game_list.pkl'), 'rb') as f:
            game_list = pickle.load(f)
        return game_list

    def should_download_appid(self, app_id: int) -> bool:
        return app_id not in self.exclude_set

    # Return True if modified, False otherwise
    def set_enable_app_id(self, app_id: int, enable: bool) -> bool:
        if app_id in self.exclude_set:
            if enable:
                self.exclude_set.remove(app_id)
                self.config['Target']['list'] = list(self.exclude_set)
            else:
                return False
        else:
            if enable:
                return False
            else:
                self.config['Target']['list'].append(app_id)

        self.config_client.export_to_file(self.config, core.s_config_file)
        self.reload_config()
        return True