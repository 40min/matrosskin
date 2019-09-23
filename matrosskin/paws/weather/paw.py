import logging
from datetime import (
    timedelta,
    datetime
)

from telegram.bot import Bot
from telegram.update import Update
from telegram.ext.dispatcher import run_async
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

from matrosskin.l10n import _
from matrosskin.paws.generic import (
    Paw,
    location_handler,
    handle_location
)
from matrosskin.paws.markups import request_geo_markup
from matrosskin.modules.storage import user_data_storage
from utils.common import get_user_data_from_update

from .forecasts import (
    day_forecast,
    multiple_days_forecast
)

logger = logging.getLogger(__name__)

WEATHER_SHARE_LOCATION = _("Would you mind sharing your location to show weather?")
WEATHER_FORECAST_SHARE_LOCATION = _("Would you mind sharing your location to show weather forecast?")
USER_LOCATION_FRESHNESS_PERIOD = 3600

weather_by_coords_mapping = {
    WEATHER_SHARE_LOCATION: day_forecast,
    WEATHER_FORECAST_SHARE_LOCATION: multiple_days_forecast
}


def weather_request_with_update_location(bot: Bot, update: Update, forecast: bool = False) -> None:
    logger.info('/weather_loc command')

    request_text = WEATHER_FORECAST_SHARE_LOCATION if forecast else WEATHER_SHARE_LOCATION
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=request_text,
        reply_markup=request_geo_markup
    )


def user_location_is_actual(update_dtime: datetime) -> bool:
    return datetime.utcnow() < update_dtime + timedelta(seconds=USER_LOCATION_FRESHNESS_PERIOD)


def weather_request(bot: Bot, update: Update, city: str = None, period_forecast: bool = False) -> None:
    logger.info('/weather command')

    chat_id = update.message.chat_id
    forecast_obj = multiple_days_forecast if period_forecast else day_forecast
    if city:
        message_answer = forecast_obj.get_by_city(city)
    else:
        user_data = user_data_storage.get(chat_id)
        if user_data and user_location_is_actual(user_data.updated):
            message_answer = forecast_obj.get_by_coords(user_data.coordinates)
        else:
            weather_request_with_update_location(bot, update, period_forecast)
            return

    bot.send_message(chat_id=chat_id, text=message_answer)


@location_handler
@run_async
def get_location(update: Update, context: CallbackContext) -> None:
    user_data = get_user_data_from_update(update)
    user_data_storage.save(user_data)

    if update.message.reply_to_message.text and \
            update.message.reply_to_message.text in weather_by_coords_mapping:
        chat_id = update.message.chat_id
        message_answer = weather_by_coords_mapping[update.message.reply_to_message.text].get_by_coords(
            coords=user_data.coordinates
        )
        context.bot.send_message(chat_id=chat_id, text=message_answer)


@run_async
def weather_request_async(update: Update, context: CallbackContext) -> None:
    weather_request(context.bot, update)


@run_async
def weather_forecast_request_async(update: Update, context: CallbackContext) -> None:
    weather_request(context.bot, update, period_forecast=True)


@run_async
def weather_request_with_update_location_async(update: Update, context: CallbackContext) -> None:
    weather_request_with_update_location(context.bot, update)\


@run_async
def weather_forecst_request_with_update_location_async(update: Update, context: CallbackContext) -> None:
    weather_request_with_update_location(context.bot, update, forecast=True)


class WeatherPaw(Paw):
    name = 'weather'
    handlers = {
        CommandHandler(['w'], weather_request_async),
        CommandHandler(['wf'], weather_forecast_request_async),
        CommandHandler(['wl'], weather_request_with_update_location_async),
        CommandHandler(['wfl'], weather_forecst_request_with_update_location_async),
        MessageHandler(Filters.location, handle_location)
    }
