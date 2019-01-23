import redis
from collections import namedtuple

from modules.settings import config

STORAGE_USER_PREFIX = 'user'

Coordinates = namedtuple('Coordinates', ['latitude', 'longitude'])

pool = redis.ConnectionPool(host=config['host'], port=config['port'], db=config['db'])
redis_storage = redis.Redis(connection_pool=pool)


def get_storage_user_prefix(username):
    return f'{STORAGE_USER_PREFIX}_{username}'


def save_user_location_to_store(username, coords):
    key = get_storage_user_prefix(username)
    redis_storage.hmset(
        key,
        {
            'latitude': coords.latitude,
            'longitude': coords.longitude
        }
    )


def get_user_location_from_store(username):
    key = get_storage_user_prefix(username)
    stored_data = redis_storage.hgetall(key)
    if not stored_data:
        return None
    coordinates = Coordinates(float(stored_data[b'latitude']), float(stored_data[b'longitude']))
    return coordinates
