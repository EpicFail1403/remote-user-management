import configparser
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


class User:
    def __init__(self, name: str, key: str) -> None:
        self.name: str = name
        self.key: str = key


def load_from_ini(config) -> Dict[str, User]:
    if isinstance(config, (str, bytes, os.PathLike)):
        config_parser = configparser.ConfigParser()
        config_parser.read(config)
    elif isinstance(config, configparser.ConfigParser):
        config_parser: configparser.ConfigParser = config
    else:
        raise "invalid config"

    result: Dict[User] = {}

    logger.info("loading users from {}".format(config))
    for user_name in config_parser.sections():
        if user_name == "DEFAULT":
            continue

        user = User(user_name, config_parser[user_name]["key"])
        result[user_name] = user
        logger.info(user_name)

    return result
