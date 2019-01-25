import logging

import pyowm
from pyowm.weatherapi25.observation import Observation
from pyowm.exceptions.api_response_error import NotFoundError

from telegram.bot import Bot
from telegram.update import Update
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
WEATHER_SHARE_LOCATION = 'Would you mind sharing your location to show weather?'
WEATHER_FORECAST_SHARE_LOCATION = 'Would you mind sharing your location to show weather forecast?'


request_geo_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton('Approve', request_location=True)]
    ],
    one_time_keyboard=True
)


def get_weather_txt(observation: Observation, location_name: str) -> str:
    weather_lookup = observation.get_weather()
    day = WeatherDay.   create_from_weather_lookup(weather_lookup)

    weather_txt = f"""
        Weather for location {location_name}
        {day.get_formatted()}
        """

    return weather_txt


def get_weather_forecast_txt(observations, location_name: str) -> str:
    forecast = WeatherForecast(location_name, observations)
    weather_txt = f"""
            {forecast.get_formatted()}
            """
    return weather_txt


def get_weather_by_city(city: str) -> str:
    try:
        observation = owm.weather_at_place(city)
    except NotFoundError:
        city_from_local_mapping = city_to_geoid_mapping.get_city_geoid(city)
        if not city_from_local_mapping:
            return WEATHER_NOT_FOUND_MESSAGE

        observation = owm.weather_at_id(city_from_local_mapping)

    weather_txt = get_weather_txt(observation, location_name=city)
    return weather_txt


def get_weather_by_coords(coords: Coordinates) -> str:
    try:
        observation = owm.weather_at_coords(lat=coords.latitude, lon=coords.longitude)
        location = observation.get_location()
        location_txt = f'{location.get_country()} - {location.get_name()}'
    except NotFoundError:
        return WEATHER_NOT_FOUND_MESSAGE

    weather_txt = get_weather_txt(observation, location_txt)
    return weather_txt


# owm.three_hours_forecast(name='')
def get_weather_forecast_by_coords(coords: Coordinates) -> str:
    forecaster = owm.three_hours_forecast_at_coords(lat=coords.latitude, lon=coords.longitude)
    if not forecaster:
        return WEATHER_NOT_FOUND_MESSAGE

    weathers = forecaster.get_forecast().get_weathers()
    location = forecaster.get_forecast().get_location()
    location_txt = f'{location.get_country()} - {location.get_name()}'
    weather_txt = get_weather_forecast_txt(weathers, location_txt)

    return weather_txt


def get_weather_forecast_by_city(city: str) -> str:
    forecaster = owm.three_hours_forecast(name=city)
    if not forecaster:
        geoid = city_to_geoid_mapping.get_city_geoid(city)
        if not geoid:
            return WEATHER_NOT_FOUND_MESSAGE
        forecaster = owm.three_hours_forecast_at_id(geoid)
        if not forecaster:
            return WEATHER_NOT_FOUND_MESSAGE

    weathers = forecaster.get_forecast().get_weathers()
    weather_txt = get_weather_forecast_txt(weathers, location_name=city)

    return weather_txt


def weather_request_with_update_location(bot: Bot, update: Update, forecast: bool = False) -> None:
    logger.info('/weather_loc command')

    request_text = WEATHER_FORECAST_SHARE_LOCATION if forecast else WEATHER_SHARE_LOCATION
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=request_text,
        reply_markup=request_geo_markup
    )


def weather_request(bot: Bot, update: Update, city: str = None, forecast: bool = False) -> None:
    logger.info('/weather command')

    username = update.message.from_user.username
    chat_id = update.message.chat_id

    if city:
        if forecast:
            message_answer = get_weather_forecast_by_city(city)
        else:
            message_answer = get_weather_by_city(city)
        bot.send_message(chat_id=chat_id, text=message_answer)
        return
    else:
        coords = user_data_storage.get_user_location_from_store(username)
        if coords:
            if forecast:
                message_answer = get_weather_forecast_by_coords(coords)
            else:
                message_answer = get_weather_by_coords(coords)
            bot.send_message(chat_id=chat_id, text=message_answer)
            return

    weather_request_with_update_location(bot, update, forecast)


weather_by_coords_answer_methods = {
    WEATHER_SHARE_LOCATION: get_weather_by_coords,
    WEATHER_FORECAST_SHARE_LOCATION: get_weather_forecast_by_coords
}


@run_async
def weather_request_async(bot: Bot, update: Update) -> None:
    weather_request(bot, update)


@run_async
def weather_forecast_request_async(bot: Bot, update: Update) -> None:
    weather_request(bot, update, forecast=True)


@run_async
def weather_request_with_update_location_async(bot: Bot, update: Update) -> None:
    weather_request_with_update_location(bot, update)\


@run_async
def weather_forecst_request_with_update_location_async(bot: Bot, update: Update) -> None:
    weather_request_with_update_location(bot, update, forecast=True)


@run_async
def get_location(bot: Bot, update: Update, user_data) -> None:
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.message.from_user.username
    coords = Coordinates(latitude, longitude)

    user_data_storage.save_user_location_to_store(username, coords)

    if update.message.reply_to_message.text and \
            update.message.reply_to_message.text in weather_by_coords_answer_methods:
        chat_id = update.message.chat_id
        answer_method = weather_by_coords_answer_methods[update.message.reply_to_message.text]
        message_answer = answer_method(coords=coords)
        bot.send_message(chat_id=chat_id, text=message_answer)


class WeatherPaw(Paw):
    name = 'weather'
    handlers = {
        CommandHandler(['weather', 'w'], weather_request_async),
        CommandHandler(['weather', 'wf'], weather_forecast_request_async),
        CommandHandler(['weather_loc', 'wl'], weather_request_with_update_location_async),
        CommandHandler(['weather_loc', 'wfl'], weather_forecst_request_with_update_location_async),
        MessageHandler(Filters.location, get_location, pass_user_data=True)
    }
