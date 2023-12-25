from functools import lru_cache
import os
import random
import string

from pydantic import BaseSettings
from dotenv import dotenv_values
from app.configs.exceptions import *


@lru_cache
def load_env() -> None:
    env = os.environ.get('PATH_TO_ENV')
    if os.path.isfile(env):
        env_dict = dict(dotenv_values(env))
        for key in env_dict.keys():
            os.environ[key] = env_dict[key]
    elif os.environ.get('OS_CONFIGS'):
        pass
    else:
        raise ConfigLoadDotenvError('Invalid env`s path')


class EnvironmentSettings(BaseSettings):
    API_VERSION: str
    APP_NAME: str
    PATH_TO_STORAGE: str
    DEBUG_MODE: bool
    DB_REPOSITORY_ENDPOINT: str

    class Config:
        load_env()
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables():
    return EnvironmentSettings()


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str
