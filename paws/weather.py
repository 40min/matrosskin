import logging

from telegram.ext import CommandHandler
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler, Filters

from weather import Weather, Unit


logger = logging.getLogger(__name__)
weather = Weather(unit=Unit.CELSIUS)
locations = {}

request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton('Approve', request_location=True)]
    ],
    one_time_keyboard=True
)


def save_location_to_store(username, latitude, longitude):
    locations[username] = [latitude, longitude]


def get_location_from_store(username):
    return locations.get(username, [None, None])


def weather_message(bot, latitude, longitude, chat_id):
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
    bot.send_message(chat_id=chat_id, text=message_answer)


def weather_request_with_update_location(bot, update):
    logger.info('/weather_loc command')

    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Would you mind sharing your location with me?',
        reply_markup=request_geo_markup
    )


def weather_request(bot, update):
    logger.info('/weather command')

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    latitude, longitude = get_location_from_store(username)

    if latitude and longitude:
        weather_message(bot, latitude, longitude, chat_id)
    else:
        weather_request_with_update_location(bot, update)


def get_location(bot, update, user_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.message.from_user.username

    save_location_to_store(username, latitude, longitude)
    weather_message(bot, latitude, longitude, update.message.chat_id)


class Paw:
    name = 'weather'
    handlers = (
        CommandHandler(['weather', 'w'], weather_request),
        CommandHandler(['weather_loc', 'wl'], weather_request_with_update_location),
        MessageHandler(Filters.location, get_location, pass_user_data=True)
    )
