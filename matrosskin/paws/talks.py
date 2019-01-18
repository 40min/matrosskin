import logging
import json
from collections import namedtuple

import apiai
from telegram.ext import (
    MessageHandler,
    Filters
)
from telegram.ext.dispatcher import run_async

from .generic import Paw
from .news import get_news
from .weather.paw import weather_request
from modules.settings import config

DONT_UNDERSTAND_PHRASE = 'Mrrr .... ?'
IDK_ANSWER = 'idk'


class ProcessingResult:
    def __init__(self, answer_txt=None, processed=False):
        self.answer_txt = answer_txt
        self.processed = processed


logger = logging.getLogger(__name__)
agents = {
    'smalltalk': config['df_client_smalltalk_token'],
    'weather': config['df_client_weather_token']
}


def get_news_action(bot, update):
    return get_news()


def get_weather_action(bot, update):
    weather_request(bot, update)
    return None


paws_mapping = {
    'news': get_news_action,
    'weather': get_weather_action
}


def proceed_action(bot, update, action):
    action = action.split('.')[0]
    if action in paws_mapping:
        answer_txt = paws_mapping[action](bot, update)
        return ProcessingResult(answer_txt=answer_txt, processed=True)
    return ProcessingResult()


def ask_to_agent(bot, update, agent_name):
    request = apiai.ApiAI(agents[agent_name]).text_request()
    request.lang = config['lang']
    request.session_id = config['session_id']

    request.query = update.message.text
    response_json = json.loads(request.getresponse().read().decode('utf-8'))
    if response_json['result'].get('action'):
        result = proceed_action(bot, update, response_json['result']['action'])
        if result.processed:
            return result

    response_txt = response_json['result']['fulfillment']['speech']
    if not response_txt or response_txt == IDK_ANSWER:  # agent answered IDK_ANSWER means it have no idea how to handle
        return ProcessingResult()
    return ProcessingResult(answer_txt=response_txt, processed=True)


@run_async
def proceed_phrase(bot, update):
    for agent in agents:
        result = ask_to_agent(bot, update, agent)
        if result.processed:
            if result.answer_txt:
                bot.send_message(chat_id=update.message.chat_id, text=result.answer_txt)
            return
    bot.send_message(chat_id=update.message.chat_id, text=DONT_UNDERSTAND_PHRASE)


class TalksPaw(Paw):
    name = 'talks'
    handlers = {
        MessageHandler(Filters.text, proceed_phrase)
    }
