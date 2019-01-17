import logging

import pyowm
from pyowm.exceptions.api_response_error import NotFoundError
from telegram.ext.dispatcher import run_async
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters
)
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup
)

from paws.generic import Paw
from modules.settings import config
from modules.storage import redis_storage
from .classes import (
    WeatherDay,
    WeatherForecast,
    Coordinates
)

logger = logging.getLogger(__name__)
owm = pyowm.OWM(API_key=config['owm_api_key'], language=config['owm_language'])

WEATHER_NOT_FOUND_MESSAGE = 'weather not found'
STORAGE_PREFIX = 'weather'

request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton('Approve', request_location=True)]
    ],
    one_time_keyboard=True
)


def get_storage_news_prefix(username):
    return f'{STORAGE_PREFIX}_{username}'


def save_location_to_store(username, coords):
    key = get_storage_news_prefix(username)
    redis_storage.hmset(
        key,
        {
            'latitude': coords.latitude,
            'longitude': coords.longitude
        }
    )


def get_location_from_store(username):
    key = get_storage_news_prefix(username)
    stored_data = redis_storage.hgetall(key)
    if not stored_data:
        return None
    coordinates = Coordinates(float(stored_data[b'latitude']), float(stored_data[b'longitude']))
    return coordinates


def _get_weather_txt(city=None, coords=None):
    try:
        if city:
            location_txt = city
            observation = owm.weather_at_place(city)
        else:
            observation = owm.weather_at_coords(lat=coords.latitude, lon=coords.longitude)
            location = observation.get_location()
            location_txt = f'{location.get_country()} - {location.get_name()}'
    except NotFoundError:
        return WEATHER_NOT_FOUND_MESSAGE

    weather_lookup = observation.get_weather()
    day = WeatherDay(weather_lookup)

    weather_txt = f"""
    Weather for location {location_txt}
    {day.get_formatted()}
    """

    return weather_txt


def get_weather_by_city(city):
    return _get_weather_txt(city)


def get_weather_by_coords(coords):
    return _get_weather_txt(coords=coords)


def weather_message(bot, coords, chat_id):
    #fc = owm.three_hours_forecast_at_coords(lat=latitude, lon=longitude)
    message_answer = get_weather_by_coords(coords)
    bot.send_message(chat_id=chat_id, text=message_answer)


@run_async
def weather_request_with_update_location(bot, update):
    logger.info('/weather_loc command')

    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Would you mind sharing your location with me?',
        reply_markup=request_geo_markup
    )

@run_async
def weather_request(bot, update):
    logger.info('/weather command')

    username = update.message.from_user.username
    chat_id = update.message.chat_id
    coords = get_location_from_store(username)

    if coords:
        weather_message(bot, coords, chat_id)
    else:
        weather_request_with_update_location(bot, update)


@run_async
def get_location(bot, update, user_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.message.from_user.username
    coords = Coordinates(latitude, longitude)

    save_location_to_store(username, coords)

    weather_message(bot, coords, update.message.chat_id)


class WeatherPaw(Paw):
    name = 'weather'
    handlers = {
        CommandHandler(['weather', 'w'], weather_request),
        CommandHandler(['weather_loc', 'wl'], weather_request_with_update_location),
        MessageHandler(Filters.location, get_location, pass_user_data=True)
    }
