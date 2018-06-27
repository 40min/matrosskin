import logging

from telegram.ext import CommandHandler
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters

from weather import Weather, Unit


logger = logging.getLogger(__name__)
weather = Weather(unit=Unit.CELSIUS)

request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton('Approve', request_location=True)]
    ],
    one_time_keyboard=True
)


def weather_message(bot, update):
    logger.info('/weather command')

    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Would you mind sharing your location with me?',
        reply_markup=request_geo_markup
    )


def get_location(bot, update, user_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    lookup = weather.lookup_by_latlng(latitude, longitude)
    city = lookup.location.city
    condition = lookup.condition
    # see lookup.forecast lookup.atmosphere
    temperature = lookup.condition.temp
    humidity = lookup.atmosphere['humidity']

    message_answer = f"""
        Weather for {city}:

        - condition: {condition.text} 
        - temperature: {temperature}
        - humidity: {humidity}
    """

    bot.send_message(chat_id=update.message.chat_id, text=message_answer)


class Paw:
    name = 'weather'
    handlers = (
        CommandHandler(['weather', 'w'], weather_message),
        MessageHandler(Filters.location, get_location, pass_user_data=True)
    )
