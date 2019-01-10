import logging
from datetime import datetime

from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async

from analner.news_maker import FunMaker
from analner.head_grab import HeadGrab, TARGET_URL

from modules.settings import config
from .generic import (
    Paw,
    Job
)

DEFAULT_NEWS = 'no news at all (((('

logger = logging.getLogger(__name__)

data_path = config['data_path']
if not data_path:
    raise Exception("Please setup path to storing data [data_path] var")

dropbox_token = config.get('dropbox_token')

fun_generator = FunMaker(data_path, dropbox_token)
head_grab = HeadGrab(data_path, TARGET_URL, dropbox_token)

subscribed_chats = set()


def grab_news_callback(bot, job):
    now = datetime.now()
    logger.info('Grabbing news {}' . format(now.strftime('%Y-%m-%d %H:%M:%S')))
    news_added = head_grab.run()
    if news_added:
        fun_generator.reload_model_from_txt()


def subscribed_generate_callback(bot, job):
    for chat_id in subscribed_chats:
        fun_txt = fun_generator.make_phrases()
        if fun_txt:
            bot.send_message(chat_id=chat_id, text=fun_txt[0].encode('utf-8'))


@run_async
def show_news(bot, update):
    phrases = fun_generator.make_phrases()
    news_phrase = phrases[0] if phrases else DEFAULT_NEWS
    bot.send_message(chat_id=update.message.chat_id, text=news_phrase)


def subscribe(bot, update):
    chat_id = update.message.chat_id
    subscribed_chats.add(chat_id)


def unsubscribe(bot, update):
    chat_id = update.message.chat_id
    subscribed_chats.remove(chat_id)


class NewsPaw(Paw):
    name = 'Analner news'
    handlers = {
        CommandHandler(['news', 'n'], show_news),
        CommandHandler(['subs'], subscribe),
        CommandHandler(['unsubs'], unsubscribe),
    }
    jobs = {
        Job(callback=grab_news_callback, interval=60*60*6, first=0),
        Job(callback=subscribed_generate_callback, interval=5, first=1)
    }
