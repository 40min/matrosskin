from telegram.ext import Updater
from modules.settings import config

updater = Updater(token=config['tg_token'])
dispatcher = updater.dispatcher
