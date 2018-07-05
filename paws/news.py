import logging

from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async


logger = logging.getLogger(__name__)


@run_async
def show_news(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text='new news underconstruction')


class Paw:
    name = 'Analner news'
    handlers = (
        CommandHandler(['news', 'n'], show_news),
    )
