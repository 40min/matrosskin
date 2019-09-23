from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from matrosskin.l10n import _


def yes_no_markup():
    keyboard = [
        [
            InlineKeyboardButton(_("yes"), callback_data='1'),
            InlineKeyboardButton(_("no"), callback_data='0')
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton(_("Requested location"), request_location=True)]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)
