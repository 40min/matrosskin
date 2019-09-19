from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def yes_no_markup():
    keyboard = [
        [
            InlineKeyboardButton(_("yes"), callback_data='1'),
            InlineKeyboardButton(_("no"), callback_data='0')
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
