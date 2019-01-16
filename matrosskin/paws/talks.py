import logging
import json

import apiai
from telegram.ext import (
    MessageHandler,
    Filters
)
from telegram.ext.dispatcher import run_async

from .generic import Paw
from .news import get_news
from modules.settings import config

logger = logging.getLogger(__name__)

DONT_UNDERSTAND_PHRASE = 'Mrrr .... ?'
IDK_ANSWER = 'idk'
agents = {
    'smalltalk': config['df_client_smalltalk_token'],
    'weather': config['df_client_weather_token']
}

paws_mapping = {
    'paw_news': get_news
}


def ask_to_agent(update, agent_name):
    request = apiai.ApiAI(agents[agent_name]).text_request()
    request.lang = config['lang']
    request.session_id = config['session_id']

    request.query = update.message.text
    response_json = json.loads(request.getresponse().read().decode('utf-8'))
    response_txt = response_json['result']['fulfillment']['speech']
    if response_txt and response_txt == IDK_ANSWER:
        response_txt = None
    return response_txt


@run_async
def proceed_phrase(bot, update):
    for agent in agents:
        response_txt = ask_to_agent(update, agent)
        if response_txt:
            if response_txt.startswith('paw_') and response_txt in paws_mapping:
                response_txt = paws_mapping[response_txt]()
            bot.send_message(chat_id=update.message.chat_id, text=response_txt)
            return
    bot.send_message(chat_id=update.message.chat_id, text=DONT_UNDERSTAND_PHRASE)


class TalksPaw(Paw):
    name = 'talks'
    handlers = {
        MessageHandler(Filters.text, proceed_phrase)
    }
