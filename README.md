### BotsAnywhere: Deploying Telegram bots to PythonAnywhere
This script helps streamlining the process of deploying one or more Telegram bots to a PythonAnywhere instance.

#### Requirements
- Currently, the bot must be built using [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/).
- During the initialization, `threaded` **must** be set to `False`; at least for the free tier in PythonAnywhere.
- The bot instance must be accessible from outside the module: `from bot_module import bot` is used in the loader.

#### Usage
First, this repository must be cloned:
```bash
git clone https://github.com/aban-m/BotsAnywhere
```
Then the 'Source code' in the web app setup is set to `flask_app.py`.

##### Configuration
Then, two files must be created *in the BotsAnywhere directory*, `config.ini` and a file listing the bots to be loaded, whose path is specified by the `bots` variable in `config.ini`.

config.ini:
```ini
[config]
bots=bots.ini
host=https://yourhostname.pythonanywhere.com
```

The `bots.ini` file consists of a list of sections, one for each bot.  It has the format:
```ini
[bot1]
package=bot1pkg
export_name=bot
path=..
endpoint=/bot1-<rand>

[bot2]
[bot3]
```

All four variables are optional. `package` defaults to the section name (`bot1` in this case). `export_name` defaults to `bot`, `path` defaults to the current path, and `endpoint` defaults to `/<token>`. During processing, `<token>` is replaced by the bot token, and `<rand>` by a random alphanumeric string.


#### How it works
The bots are loaded dynamically. Then a [webhook](https://core.telegram.org/bots/webhooks) is set up for each one, based on a given (or dynamically generated) endpoint, and is registered in the Flask app.
