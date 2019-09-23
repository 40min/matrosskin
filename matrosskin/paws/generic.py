from collections import namedtuple
from functools import wraps

from telegram import Update
from telegram.ext import CallbackContext

Job = namedtuple('Job', ['callback', 'interval', 'first'])


class Paw:
    name = 'generic paw'
    handlers = set()
    jobs = set()


location_handlers = set()


def location_handler(handler):
    location_handlers.add(handler)
    @wraps
    def wrapper(*args, **kwargs):
        return handler(*args, **kwargs)
    return wrapper


def handle_location(update: Update, context: CallbackContext) -> None:
    for lh in location_handlers:
        lh(update, context)
