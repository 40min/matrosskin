import logging
from datetime import datetime

from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async

from analner.news_maker import FunMaker
from analner.head_grab import HeadGrab, TARGET_URL

from modules.settings import config
from modules.storage import redis_storage

from .generic import (
    Paw,
    Job
)

DEFAULT_NEWS = 'no news at all (((('
SUBSCRIBE_PREFIX = 'news_subscribe'

logger = logging.getLogger(__name__)

data_path = config['data_path']
if not data_path:
    raise Exception("Please setup path to storing data [data_path] var")

dropbox_token = config.get('dropbox_token')

fun_generator = FunMaker(data_path, dropbox_token)
head_grab = HeadGrab(data_path, TARGET_URL, dropbox_token)


def get_storage_subscribe_key(chat_id):
    return f'{SUBSCRIBE_PREFIX}_{chat_id}'


def grab_news_callback(bot, job):
    now = datetime.now()
    logger.info('News: Grabbing news {}' . format(now.strftime('%Y-%m-%d %H:%M:%S')))
    news_added = head_grab.run()
    if news_added:
        fun_generator.reload_model_from_txt()


def subscribed_generate_callback(bot, job):
    for subs in redis_storage.scan(match=f'{SUBSCRIBE_PREFIX}*'):
        pass

    # stopping here

    # for chat_id in subscribed_chats:
    #     logger.info(f'News: send news to chat {chat_id}')
    #     fun_txt = fun_generator.make_phrases()
    #     if fun_txt:
    #         bot.send_message(chat_id=chat_id, text=fun_txt[0])


@run_async
def show_news(bot, update):
    logger.info(f'News: single news request for user {update.message.from_user.username}')
    phrases = fun_generator.make_phrases()
    news_phrase = phrases[0] if phrases else DEFAULT_NEWS
    bot.send_message(chat_id=update.message.chat_id, text=news_phrase)


def subscribe(bot, update):
    logger.info(f'News: subscribed user {update.message.from_user.username}')
    chat_id = update.message.chat_id
    key = get_storage_subscribe_key(chat_id)
    redis_storage.hmset(key, {'chat_id': chat_id})


def unsubscribe(bot, update):
    logger.info(f'News: unsubscribed user {update.message.from_user.username}')
    chat_id = update.message.chat_id
    key = get_storage_subscribe_key(chat_id)
    redis_storage.delete(key)


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
