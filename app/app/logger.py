import os
import sys
import logging


def get_logger():
    logger_ = logging.getLogger('root')

    if os.environ.get('LOGGING_LEVEL').lower() == 'info':
        logger_.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
    elif os.environ.get('LOGGING_LEVEL').lower() == 'debug':
        logger_.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
    else:
        raise ValueError('Wrong level environment variable!')

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger_.addHandler(handler)

    return logger_


logger = get_logger()
