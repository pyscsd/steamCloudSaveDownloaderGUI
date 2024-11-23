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
        self.config = config(core.s_config_file).get_conf()
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