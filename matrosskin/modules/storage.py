from collections import namedtuple
from typing import Optional

import redis
import config

Coordinates = namedtuple('Coordinates', ['latitude', 'longitude'])

pool = redis.ConnectionPool(host=config.redis_host, port=config.redis_port, db=config.redis_db)
redis_storage = redis.Redis(connection_pool=pool)


class UserDataStorage:
    """
    Storage class to work with user details
    """
    STORAGE_USER_PREFIX = 'user'

    def get_storage_user_prefix(self, username: str) -> str:
        return f'{self.STORAGE_USER_PREFIX}_{username}'

    def save_user_location_to_store(self, username: str, coords: Coordinates) -> None:
        key = self.get_storage_user_prefix(username)
        redis_storage.hmset(
            key,
            {
                'latitude': coords.latitude,
                'longitude': coords.longitude
            }
        )

    def get_user_location_from_store(self, username: str) -> Optional[Coordinates]:
        key = self.get_storage_user_prefix(username)
        stored_data = redis_storage.hgetall(key)
        if not stored_data:
            return None
        coordinates = Coordinates(float(stored_data[b'latitude']), float(stored_data[b'longitude']))
        return coordinates


class CityNameToGeoIdMappingStorage:
    """
    Storage class to work with mapping of city names to their geonameids
    """

    MAPPING_KEY = 'cities_name_geoid_mapping'

    def add_city(self, name: str, geoid: str) -> None:
        redis_storage.hmset(self.MAPPING_KEY, {name: geoid})

    def get_city_geoid(self, name: str) -> Optional[str]:
        city_geoid = redis_storage.hget(self.MAPPING_KEY, name)
        if not city_geoid:
            return None
        return int(city_geoid)

    def is_mapping_exists(self) -> bool:
        return redis_storage.hlen(self.MAPPING_KEY) > 0


city_to_geoid_mapping = CityNameToGeoIdMappingStorage()
user_data_storage = UserDataStorage()
