from importlib import import_module
import logging
import sys
from configparser import ConfigParser


logger = logging.getLogger('loader')
DEFAULT_CONFIG = {
    'path': '.',        # where to look for the package
    'package': None,            # default package = bot name
    'export_name': 'bot',       # the variable holding the Bot instance
    'endpoint': '/<token>'      # default endpoint in the Flask app
}

def load_config_file(path: str) -> dict:
    config = ConfigParser()

    logger.debug(f'Loading path {path}.')
    config.read(path)

    out = {}

    for bot_name in config.sections():
        logger.debug(f'Processing {bot_name}...')
        # first load the defaults, then update them
        this_config = DEFAULT_CONFIG.copy()
        this_config.update(config[bot_name])
        
        if not this_config['package']:
            # package name not set, default to bot name
            this_config['package'] = bot_name

        # register bot
        out[bot_name] = this_config

    logger.debug(f'Read the metadata of {len(out)} bots.')

    return out

def load_bots(config: dict) -> dict:
    bots = {}

    for bot_name, bot_config in config.items():
        # import the relevant bot object
        _result = {}
        package = bot_config['package']
        
        sys.path.insert(0, bot_config['path'])
        logger.debug(f'Moved to {bot_config["path"]}. Importing {package}.')
        try:
            bot = getattr(import_module(package), 'bot', None)
        except Exception as e:
            raise e
        finally:
            sys.path.pop(0)

        if not bot:
            raise NameError(f'Bot was not exported from {package} under {bot_config["export_name"]}.')

        # loaded bot
        logger.debug(f'{package} imported successfully.')
        bots[bot_name] = bot

    return bots
