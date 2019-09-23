# coding=utf-8

import logging

from telegram import Update, User
from telegram.ext import (
    CommandHandler,
    CallbackContext,
    run_async,
    MessageHandler,
    Filters
)

from matrosskin.l10n import _
from matrosskin.paws.generic import (
    Paw,
    location_handler,
    handle_location
)
from matrosskin.paws.markups import request_geo_markup
from matrosskin.modules.storage import (
    user_data_storage,
    location_request_registry
)
from matrosskin.utils.sanitizers import sanitize_for_redis
from utils.common import get_user_data_from_update

logger = logging.getLogger(__name__)
GOOGLE_MAPS_LINK = "http://www.google.com/maps/place"


def get_requester_name(from_user: User) -> str:
    if from_user.username:
        return from_user.username
    elif from_user.first_name or from_user.last_name:
        return f"{from_user.first_name} {from_user.last_name}"
    return _("Unknown user")


@run_async
def find_request(update: Update, context: CallbackContext):
    if not context.args:
        context.bot.send_message(chat_id=update.message.chat_id, text=_("Please enter nickname"))
    nickname = sanitize_for_redis(context.args[0])
    user_data = user_data_storage.get_by_username(nickname)
    if not user_data:
        context.bot.send_message(chat_id=update.message.chat_id, text=_("User did not contact with Matrosskin yet"))
        return
    location_request_registry.add_location_request(chat_id_src=user_data.chat_id, chat_id_dst=update.message.chat_id)
    requester_name = get_requester_name(update.message.from_user)
    request_text = _("{username} requests for you location").format(username=requester_name)

    context.bot.send_message(
        chat_id=user_data.chat_id,
        text=request_text,
        reply_markup=request_geo_markup
    )


@location_handler
@run_async
def show_location(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message.text and \
            update.message.reply_to_message.text.endswith(_("requests for you location")):
        user_data = get_user_data_from_update(update)
        user_data_storage.save(user_data)
        chat_id_dst = location_request_registry.get_location_request(update.message.chat_id)
        if chat_id_dst:
            message = f"{GOOGLE_MAPS_LINK}/{user_data.coordinates.latitude},{user_data.coordinates.longitude}"
            context.bot.send_message(chat_id=chat_id_dst, text=message)


class FriendFinderPaw(Paw):
    name = 'friend_finder'
    handlers = {
        CommandHandler('find', callback=find_request),
        MessageHandler(Filters.location, handle_location)
    }
