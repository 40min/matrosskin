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


def grab_news_callback(bot, job):
    now = datetime.now()
    logger.info('Grabbing news {}' . format(now.strftime('%Y-%m-%d %H:%M:%S')))
    news_added = head_grab.run()
    if news_added:
        fun_generator.reload_model_from_txt()


@run_async
def show_news(bot, update):
    phrases = fun_generator.make_phrases()
    news_phrase = phrases[0] if phrases else DEFAULT_NEWS
    bot.send_message(chat_id=update.message.chat_id, text=news_phrase)


class NewsPaw(Paw):
    name = 'Analner news'
    handlers = {
        CommandHandler(['news', 'n'], show_news),
    }
    jobs = {
        Job(callback=grab_news_callback, interval=60*60*6, first=0)
    }
