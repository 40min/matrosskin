import logging
import threading

from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async

from bot import updater
from modules.settings import config
from .generic import Paw

logger = logging.getLogger(__name__)


def shutdown():
    updater.stop()
    updater.is_idle = False


@run_async
def on_exit(bot, update):
    owner = config.get('owner')
    user_from = update.message.from_user.username
    logger.info(f"User {user_from} requests exit")
    if user_from == owner:
        logger.info('Exiting ...')
        threading.Thread(target=shutdown).start()


class OwnerPaw(Paw):
    name = 'owner'
    handlers = {
        CommandHandler(['exit', 'e'], on_exit),
    }
