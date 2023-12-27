class ConnectorRabbitConnectionError(Exception):
    """
    Error class for case when rabbit connection is interrupted
    """
    pass


class ConnectorRabbitAllowedVirtualHostError(Exception):
    """
    Error class for case when rabbit virtual host is not in whitelist
    """
    pass


class ConnectorConfigError(Exception):
    """
    Error class for case when reading config file (.env) is interrupted (structure is invalid)
    """
    pass


class ConnectorConfigPathError(Exception):
    """
    Error class for case when reading config file (.env) is interrupted (path is invalid)
    """
    pass


class ConnectorLogicError(Exception):
    """
    Error class for case when there is logic error in connecting envs
    """
    pass


class ConnectorOSVariablesLoadingError(Exception):
    """
    Error class for case when os environment variables loading is invalid
    """
    pass
