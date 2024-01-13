import logging
import logging.config
import yaml

"""
Путь к конфигу с настройками для логгирования.
"""
LOGGING_CFG_PATH = "configs/logging.cfg.yml"

"""
Функция для загрузки параметров для logging и создания объекта logging.
"""


def get_logger(logging_cfg_path: str = None):
    logger_easyocr = logging.getLogger('logger')

    with open(logging_cfg_path) as config_fin:
        logging.config.dictConfig(yaml.safe_load(config_fin.read()))

    return logger_easyocr


logger = get_logger(logging_cfg_path=LOGGING_CFG_PATH)
