import logging

from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async


logger = logging.getLogger(__name__)


@run_async
def on_someone(bot, update, groups):
    pass


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='Mrrr .... ?')


class Paw:
    name = 'awesome'
    handlers = (
        CommandHandler('start', start),
    )
