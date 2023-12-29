import os
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

import amqp
from dotenv import dotenv_values

from src import logger
from src.connector.exceptions import *


class Connection:
    """
    Base class for connection to S3, RabbitMQ and Kafka

    Args:
        connection_entity (str): name of connection entity (rabbit, s3 or kafka)

    Attributes:
        connections_config (dict): dictionary with right and allowed structure of .env files with different
            options for each entity
        envs_secrets (dict): secrets from entity .env file
        option (int): option of entity config
    """
    connections_configs = {'rabbit': {1: ['RABBIT_URL', 'INPUT_QUEUE', 'OUTPUT_AUDIO_QUEUE',
                                          'OUTPUT_FRAME_QUEUE', 'OUTPUT_API_QUEUE'],
                                      2: ['RABBIT_HOST', 'RABBIT_USERNAME', 'RABBIT_PASSWORD', 'INPUT_QUEUE',
                                          'OUTPUT_AUDIO_QUEUE', 'OUTPUT_FRAME_QUEUE', 'OUTPUT_API_QUEUE']},
                           }

    @staticmethod
    def __load_env_from_os(env: Path) -> Dict:
        if 'rabbit' in str(env):
            _vars_rabbit_1_option = {'RABBIT_URL': os.environ.get("RABBIT_URL"),
                                     'INPUT_QUEUE': os.environ.get("INPUT_QUEUE"),
                                     'OUTPUT_AUDIO_QUEUE': os.environ.get("OUTPUT_AUDIO_QUEUE"),
                                     'OUTPUT_FRAME_QUEUE': os.environ.get("OUTPUT_FRAME_QUEUE"),
                                     'OUTPUT_API_QUEUE': os.environ.get("OUTPUT_API_QUEUE")}

            return _vars_rabbit_1_option

        else:
            raise ConnectorConfigPathError('Invalid env`s path')

    @staticmethod
    def __load_env(env: Path) -> Dict:
        """
        Loading .env file
        :param env (Path): path to .env file
        :return: dict with data from .env file
        """
        if os.environ.get('OS_CONFIG'):
            return Connection.__load_env_from_os(env=env)
        if os.path.isfile(env):
            return dict(dotenv_values(env))
        else:
            raise ConnectorConfigPathError('Invalid env`s path')

    def __check_env(self, env: Path):
        """
        Checking for correctness of structure by connections_config
        :param env (Path): path to .env file
        :return (bool): is .env file structure is correct
        """
        self.envs_secrets = self.__load_env(env=env)
        _is_ok = False

        for config_option in self.connections_configs[self.connection_entity].keys():

            correct_config = self.connections_configs[self.connection_entity][config_option]

            if isinstance(correct_config, list) and list(self.envs_secrets.keys()) == correct_config:
                _is_ok = True
                self.option = config_option
        return _is_ok

    def __init__(self, connection_entity: str):
        assert connection_entity.lower() in self.connections_configs.keys(), 'Invalid connection entity'
        self.connection_entity = connection_entity

    def __call__(self, env: Path):
        if not self.__check_env(env):
            raise ConnectorConfigError('Invalid env`s config')

    def __repr__(self):
        return f'Class for {self.connection_entity} connection'


@dataclass()
class RabbitEnv:
    """
    Dataclass for creds for RabbitMQ connection with checking hosts and virtual hosts whitelists
    """
    input_queue: str = field()
    output_frame_queue: str = field()
    output_audio_queue: str = field()
    output_api_queue: str = field()
    username: str = field()
    password: str = field()
    host: str = field()
    virtual_host: str = field()

    def validate(self):
        white_virtual_hosts = ['all', '_', 'dev']
        if self.virtual_host not in white_virtual_hosts:
            raise ConnectorRabbitAllowedVirtualHostError(f'Not allowed virtual host: {self.virtual_host}')

    def __post_init__(self):
        self.validate()


class RabbitConnection(Connection):
    """
    Class for RabbitMQ connection (base class Connection inheritor)

    Args:
        see docstring in class Connection

    Attributes:
        secrets (object of RabbitEnv dataclass): object with creds for rabbit connection
    """

    def __init__(self):
        super().__init__(connection_entity='rabbit')

    def __call__(self, env: Path) -> Tuple[amqp.Connection, amqp.Channel, str, str, str, str]:
        """
        Connect to RabbitMQ
        :param env (Path): path to .env file
        :return:
            amqp.Connection
            amqp.Channel
            input rabbit queue (str)
            output rabbit queue (str)
        """
        super().__call__(env)

        if self.option == 1:
            host, virtual_host = self.envs_secrets['RABBIT_URL'].split('@')[1].split('/')
            _, username, password = self.envs_secrets['RABBIT_URL'].split('@')[0].split(':')

            self.secrets = RabbitEnv(host=host,
                                     virtual_host=virtual_host,
                                     username=username.replace('//', ''),
                                     password=password,
                                     input_queue=self.envs_secrets['INPUT_QUEUE'],
                                     output_audio_queue=self.envs_secrets['OUTPUT_AUDIO_QUEUE'],
                                     output_frame_queue=self.envs_secrets['OUTPUT_FRAME_QUEUE'],
                                     output_api_queue=self.envs_secrets['OUTPUT_API_QUEUE'])

        elif self.option == 2:
            host, virtual_host = self.envs_secrets['RABBIT_HOST'].split('/')

            self.secrets = RabbitEnv(host=host,
                                     virtual_host=virtual_host,
                                     username=self.envs_secrets['RABBIT_USERNAME'],
                                     password=self.envs_secrets['RABBIT_PASSWORD'],
                                     input_queue=self.envs_secrets['INPUT_QUEUE'],
                                     output_audio_queue=self.envs_secrets['OUTPUT_AUDIO_QUEUE'],
                                     output_frame_queue=self.envs_secrets['OUTPUT_FRAME_QUEUE'],
                                     output_api_queue=self.envs_secrets['OUTPUT_API_QUEUE'])

        else:
            raise ConnectorConfigError('Invalid env`s config')

        if self.secrets.virtual_host == '_':
            self.secrets.virtual_host = '/'

        try:
            connection = amqp.Connection(
                host=self.secrets.host,
                userid=self.secrets.username,
                password=self.secrets.password,
                virtual_host=self.secrets.virtual_host
            )

            connection.connect()
            channel = connection.channel()
        except Exception as e:
            raise ConnectorRabbitConnectionError(e)

        return connection, channel, self.secrets.input_queue, \
            self.secrets.output_audio_queue, \
            self.secrets.output_frame_queue, self.secrets.output_api_queue


class Connector:
    """
    Class interface for connection

    Args:
        path_to_rabbit_env (Path): path to rabbit .env file

    Attributes:
        rabbit_connection (amqp.Connection): rabbit connection
        rabbit_channel (amqp.Channel): rabbit channel
        rabbit_input_queue (str): name of rabbit input queue
        rabbit_output_queue (str): name of rabbit output queue
    """

    def __init__(self,
                 path_to_rabbit_env: Optional[Path] = None,
                 is_special_case: bool = False):

        if not is_special_case:
            self.__validate(path_to_rabbit_env)

        if path_to_rabbit_env is not None:
            connect_to_rabbit = RabbitConnection()
            self.rabbit_connection, self.rabbit_channel, self.rabbit_input_queue, self.rabbit_output_audio_queue, \
                self.rabbit_output_frame_queue, self.rabbit_output_api_queue = connect_to_rabbit(path_to_rabbit_env)
            logger.info('Connect to Rabbit MQ')

    @staticmethod
    def __validate(rabbit):
        if not rabbit:
            raise ConnectorLogicError('No rabbit env!')
