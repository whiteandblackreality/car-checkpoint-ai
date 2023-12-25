import os
import json
import requests

from app.configs import get_environment_variables
from app.configs.exceptions import *
from app.logger import logger
from app.schemas.schemas import *

env = get_environment_variables()


class VideosStorage:
    def __init__(self,
                 path_to_storage,
                 db_repository_endpoint):
        os.makedirs(path_to_storage, exist_ok=True)
        self.path_to_storage = path_to_storage

        self.db_repository_endpoint = db_repository_endpoint
        self._headers = {'Content-Type': 'application/json'}

    def get_path(self) -> str:
        return self.path_to_storage

    def create_video_in_db(self, path_to_video) -> VideoResponse:
        return requests.post(url=f'{self.db_repository_endpoint}/v1/videos/',
                             data=json.dumps({'video_path': path_to_video}),
                             headers=self._headers).json()

    def get_frames(self, video_id):
        return requests.get(url=f'{self.db_repository_endpoint}/v1/videos/frames_by_video_id/{video_id}').json()



try:
    VIDEOS_STORAGE = VideosStorage(path_to_storage=env.PATH_TO_STORAGE,
                                   db_repository_endpoint=env.DB_REPOSITORY_ENDPOINT)
    logger.info(f'Videos will be saved to {env.PATH_TO_STORAGE}')

except Exception as e:
    raise VideosStorageCreatingError(f'Error while creating storage in {env.PATH_TO_STORAGE}! '
                                     f'Exception: {e}')


def get_storage_connection():
    yield VIDEOS_STORAGE
