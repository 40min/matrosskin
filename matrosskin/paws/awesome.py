import logging

from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext
)

from .generic import Paw

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='Mrrr .... ?')


class AwesomePaw(Paw):
    name = 'awesome'
    handlers = {
        CommandHandler('start', start),
    }
