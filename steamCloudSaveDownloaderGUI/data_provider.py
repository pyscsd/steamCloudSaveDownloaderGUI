from .steamCloudSaveDownloader.steamCloudSaveDownloader.auth import auth
from .steamCloudSaveDownloader.steamCloudSaveDownloader.web import web
from .core import core
import pickle # TODO: Remove
import os # TODO: Remove

class data_provider:
    def __init__(self, p_config: dict) -> None:
        # TODO: Uncomment when mock finished
        '''
        self.config = p_config
        self.auth = auth(core.s_config_dir, '')
        self.auth.refresh_session()
        self.web = web(self.auth.get_session_path(), self.config['Danger Zone']['wait_interval'])
        '''


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