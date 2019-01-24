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
from modules.storage import (
    Coordinates,
    user_data_storage,
    city_to_geoid_mapping
)
from .classes import (
    WeatherDay,
    WeatherForecast
)

logger = logging.getLogger(__name__)
owm = pyowm.OWM(API_key=config['owm_api_key'], language=config['owm_language'])

WEATHER_NOT_FOUND_MESSAGE = 'weather not found'

request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton('Approve', request_location=True)]
    ],
    one_time_keyboard=True
)

#fc = owm.three_hours_forecast_at_coords(lat=latitude, lon=longitude)


def get_weather_txt(observation, location_name):
    weather_lookup = observation.get_weather()
    day = WeatherDay(weather_lookup)

    weather_txt = f"""
        Weather for location {location_name}
        {day.get_formatted()}
        """

    return weather_txt


def get_weather_by_city(city):
    try:
        observation = owm.weather_at_place(city)
    except NotFoundError:
        city_from_local_mapping = city_to_geoid_mapping.get_city_geoid(city)
        if not city_from_local_mapping:
            return WEATHER_NOT_FOUND_MESSAGE

        observation = owm.weather_at_id(city_from_local_mapping)

    weather_txt = get_weather_txt(observation, location_name=city)
    return weather_txt


def get_weather_by_coords(coords):
    try:
        observation = owm.weather_at_coords(lat=coords.latitude, lon=coords.longitude)
        location = observation.get_location()
        location_txt = f'{location.get_country()} - {location.get_name()}'
    except NotFoundError:
        return WEATHER_NOT_FOUND_MESSAGE

    weather_txt = get_weather_txt(observation, location_txt)
    return weather_txt


def weather_request_with_update_location(bot, update):
    logger.info('/weather_loc command')

    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text='Would you mind sharing your location with me?',
        reply_markup=request_geo_markup
    )


def weather_request(bot, update, city=None):
    logger.info('/weather command')

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    if city:
        message_answer = get_weather_by_city(city)
        bot.send_message(chat_id=chat_id, text=message_answer)
        return
    else:
        coords = user_data_storage.get_user_location_from_store(username)
        if coords:
            message_answer = get_weather_by_coords(coords)
            bot.send_message(chat_id=chat_id, text=message_answer)
            return

    weather_request_with_update_location(bot, update)


@run_async
def weather_request_async(bot, update):
    weather_request(bot, update)


@run_async
def weather_request_with_update_location_async(bot, update):
    weather_request_with_update_location(bot, update)


@run_async
def get_location(bot, update, user_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.message.from_user.username
    coords = Coordinates(latitude, longitude)

    user_data_storage.save_user_location_to_store(username, coords)

    chat_id = update.message.chat_id
    message_answer = get_weather_by_coords(coords=coords)
    bot.send_message(chat_id=chat_id, text=message_answer)


class WeatherPaw(Paw):
    name = 'weather'
    handlers = {
        CommandHandler(['weather', 'w'], weather_request_async),
        CommandHandler(['weather_loc', 'wl'], weather_request_with_update_location_async),
        MessageHandler(Filters.location, get_location, pass_user_data=True)
    }
