import logging
import threading

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from telegram.ext.dispatcher import run_async

import config
from bot import updater
from .generic import Paw

logger = logging.getLogger(__name__)


def shutdown():
    updater.stop()
    updater.is_idle = False


@run_async
def on_exit(update: Update, context: CallbackContext):
    owner = config.owner
    user_from = update.message.from_user.username
    logger.info(f"User {user_from} requests exit")
    if owner and user_from == owner:
        logger.info('Exiting ...')
        context.bot.send_message(chat_id=update.message.chat_id, text="bye-bye :)")
        threading.Thread(target=shutdown).start()


class OwnerPaw(Paw):
    name = 'owner'
    handlers = {
        CommandHandler(['exit', 'e'], on_exit),
    }
