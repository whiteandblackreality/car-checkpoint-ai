from functools import lru_cache
import os
from typing import Dict

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
    DATABASE_DIALECT: str
    DATABASE_HOSTNAME: str
    DATABASE_NAME: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DATABASE_USERNAME: str
    DEBUG_MODE: bool
    DATABASE_SCHEMA: str

    class Config:
        load_env()
        env_file_encoding = "utf-8"


@lru_cache
def get_environment_variables():
    return EnvironmentSettings()
