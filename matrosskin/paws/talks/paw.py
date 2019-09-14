import logging
import json
from dataclasses import dataclass
from google.protobuf.json_format import MessageToJson

from dialogflow_v2.proto.session_pb2 import QueryResult
from telegram import Update
from telegram.ext import (
    MessageHandler,
    Filters,
    CallbackContext)
from telegram.ext.dispatcher import run_async
import dialogflow_v2 as dialogflow

from paws.generic import Paw
from paws.news import get_news
from paws.weather.paw import weather_request
from paws.talks.session_storage import session_storage
import config

DONT_UNDERSTAND_PHRASE = 'Mrrr .... ?'
IDK_ANSWER = 'idk'


@dataclass
class ProcessingResult:
    answer_txt: str = None
    processed: bool = False


logger = logging.getLogger(__name__)
agents = {
    'weather': config.df_weather_project_id,
    'smalltalk': config.df_small_talk_project_id,
}
df_session_client = dialogflow.SessionsClient()


def get_news_action(bot, update, params):
    return get_news()


def get_weather_action(bot, update, params):
    params_str = MessageToJson(params)
    params = json.loads(params_str)
    city = None
    if params and params.get('address'):
        city = params.get('address').get('city')
    forecast = bool(params.get('date-time', False))
    weather_request(bot, update, city, period_forecast=forecast)
    return None


paws_mapping = {
    'news': get_news_action,
    'weather': get_weather_action
}


def proceed_action(bot, update, query_result: QueryResult):
    action = query_result.action
    if action in paws_mapping:
        answer_txt = paws_mapping[action](bot, update, query_result.parameters)
        return ProcessingResult(answer_txt=answer_txt, processed=True)
    elif query_result.fulfillment_text and IDK_ANSWER != query_result.fulfillment_text:
        return ProcessingResult(answer_txt=query_result.fulfillment_text, processed=True)
    return ProcessingResult()


def ask_agent(bot, update, agent_name):
    project_id = agents[agent_name]
    session_id = session_storage.get(update.message.from_user.username)
    language_code = config.lang

    session = df_session_client.session_path(project_id, session_id)
    text_input = dialogflow.types.TextInput(text=update.message.text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = df_session_client.detect_intent(session=session, query_input=query_input)
    proc_result = proceed_action(bot, update, response.query_result)

    return proc_result


@run_async
def proceed_phrase(update: Update, context: CallbackContext):
    for agent_name in agents:
        result = ask_agent(context.bot, update, agent_name)
        if result.processed:
            if result.answer_txt:
                context.bot.send_message(chat_id=update.message.chat_id, text=result.answer_txt)
            return
    context.bot.send_message(chat_id=update.message.chat_id, text=DONT_UNDERSTAND_PHRASE)


class TalksPaw(Paw):
    name = 'talks'
    handlers = {
        MessageHandler(Filters.text, proceed_phrase)
    }
