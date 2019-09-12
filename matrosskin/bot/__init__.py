from telegram.ext import Updater
from modules.settings import config

updater = Updater(
    token=config.get('tg_token'),
    workers=config.get('workers', 32),
    use_context=True
)
dispatcher = updater.dispatcher
