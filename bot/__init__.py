import os

from telegram.ext import Updater

token = os.environ.get('TG_TOKEN') or ''
updater = Updater(token=token)
dispatcher = updater.dispatcher
