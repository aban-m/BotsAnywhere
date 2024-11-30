from time import sleep
from configparser import ConfigParser
import flask
import telebot

try: from . import loader
except ImportError: import loader


app = flask.Flask(__name__)
CONFIG_PATH = 'config.ini'
config, bots = loader.boot(CONFIG_PATH)

HOST = config['host'].rstrip('/')

def register_bot(bot_config):
    bot = bot_config['bot']
    
    endpoint = bot_config['endpoint']
    webhook_path = HOST + endpoint
    
    current_webhook = bot.get_webhook_info().url
    if current_webhook != webhook_path:
        bot.remove_webhook()
        sleep(1)
    bot.set_webhook(webhook_path)

    def hook():
        if flask.request.headers.get('Content-Type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)

    app.add_url_rule(endpoint, hook, methods=['POST'])

def register_all_bots():
    for _, bot_config in bots.items():
        register_bot(bot_config)


@app.route('/')
def index():
    running = '<ul>' + '\n'.join(f'<li>{name}</li>' for name in bots) + '</ul>'
    return '<b>Running bots:</b><br />\n'+running

