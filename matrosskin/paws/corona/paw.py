import logging

from telegram import Update
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    run_async)

from matrosskin.paws.generic import Paw
from matrosskin.paws.corona.stats import common_stats, top_countries, by_country
from matrosskin.l10n import _

logger = logging.getLogger(__name__)


@run_async
def corona_stats_common(update: Update, context: CallbackContext):
    logger.info('/corona_stats_common command')
    file_path = common_stats()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(file_path, 'rb'))


@run_async
def corona_stats_top(update: Update, context: CallbackContext):
    logger.info('/corona_stats_top command')
    file_path = top_countries()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(file_path, 'rb'))


@run_async
def corona_stats_country(update: Update, context: CallbackContext):
    logger.info('/corona_stats_country command')
    if not context.args:
        context.bot.send_message(chat_id=update.message.chat_id, text=_("Please enter name of the country"))

    file_path = by_country(context.args[0])
    if not file_path:
        context.bot.send_message(chat_id=update.message.chat_id, text=_(f"No stats for country {context.args[0]}"))
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(file_path, 'rb'))


class CoronaPaw(Paw):
    name = 'corona_stats'
    handlers = {
        CommandHandler(['corona_stats_common', 'csc'], corona_stats_common),
        CommandHandler(['corona_stats_top', 'cst'], corona_stats_top),
        CommandHandler(['corona_stats_country', 'csctry'], corona_stats_country),
    }
