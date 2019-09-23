from telegram import Update

from modules.storage import (
    UserData,
    Coordinates
)


def get_user_data_from_update(update: Update) -> UserData:
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    username = update.message.from_user.username
    coords = Coordinates(latitude, longitude)
    user_data = UserData(
        username=username,
        chat_id=update.message.chat_id,
        coordinates=coords
    )

    return user_data
