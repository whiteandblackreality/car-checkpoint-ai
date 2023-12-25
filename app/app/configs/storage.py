import os

from app.configs import get_environment_variables
from app.configs.exceptions import *
from app.logger import logger

env = get_environment_variables()


class VideosStorage:
    def __init__(self, path_to_storage):
        os.makedirs(path_to_storage, exist_ok=True)
        self.path_to_storage = path_to_storage

    def get_path(self):
        return self.path_to_storage


try:
    VIDEOS_STORAGE = VideosStorage(path_to_storage=env.PATH_TO_STORAGE)
    logger.info(f'Videos will be saved to {env.PATH_TO_STORAGE}')

except Exception as e:
    raise VideosStorageCreatingError(f'Error while creating storage in {env.PATH_TO_STORAGE}! '
                                     f'Exception: {e}')


def get_db_connection():
    yield VIDEOS_STORAGE
