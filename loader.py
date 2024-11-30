from importlib import import_module
import sys
import logging
from configparser import ConfigParser
import random
import urllib

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
LENGTH = 8
DEFAULT_CONFIG = {
    'path': '.',                    # where to look for the package
    'package': None,                # default package = bot name
    'export_name': 'bot',           # the variable holding the Bot instance
    'endpoint': '/tg-<rand>'        # default endpoint in the Flask app (<token> also possible)
}
logger = logging.getLogger('loader')

def make_endpoint(endpoint: str, bot = None):
    endpoint = endpoint.lstrip('/')
    
    if '<token>' in endpoint:
        endpoint = endpoint.replace('<token>', bot.token)
        
    if '<rand>' in endpoint:
        rand = ''.join(random.choice(ALPHABET) for _ in range(LENGTH))
        endpoint = endpoint.replace('<rand>', rand)
        
    return '/' + urllib.parse.quote(endpoint)
    
def read_config_file(path: str) -> dict:
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
        logger.debug(f'Importing {package}.')
        try:
            bot = getattr(import_module(package), 'bot', None)
        except Exception as e:
            raise e
        finally:
            sys.path.pop(0)
            logger.debug(f'Removed path corresponding to {bot_name}.')
            
        if not bot:
            raise NameError(f'Bot was not exported from {package} under {bot_config["export_name"]}.')

        # loaded bot
        logger.debug(f'{package} imported successfully.')
        bots[bot_name] = bot

    return bots


def load(path) -> dict:
    ''' Load a list of bots from a bots.ini file '''
    config = read_config_file(path)
    bots = load_bots(config)

    for name in config:
        bot = bots[name]
        endpoint = make_endpoint(config[name]['endpoint'], bot)
        config[name]['endpoint'] = endpoint
        config[name]['bot'] = bot
        
    return config
