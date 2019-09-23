from typing import Optional
from dataclasses import dataclass
from datetime import datetime

import redis
import config

pool = redis.ConnectionPool(
    host=config.redis_host, port=config.redis_port, db=config.redis_db
)
redis_storage = redis.Redis(connection_pool=pool)


@dataclass
class Coordinates:
    latitude: float = None
    longitude: float = None


@dataclass
class UserData:
    username: str = None
    chat_id: str = None
    updated: datetime = datetime.utcnow()
    coordinates: Coordinates = None


class UserDataStorage:
    """
    Storage class to work with user details
    """

    STORAGE_USER_PREFIX = "user"
    USERNAME_CHAT_ID_KEY = "username_to_chat_id"

    def get_storage_user_prefix(self, chat_id: str) -> str:
        return f"{self.STORAGE_USER_PREFIX}_{chat_id}"

    def save(self, data: UserData) -> None:
        key = self.get_storage_user_prefix(data.chat_id)
        redis_storage.hmset(
            key,
            {
                "username": data.username,
                "latitude": data.coordinates.latitude,
                "longitude": data.coordinates.longitude,
                "updated": data.updated.isoformat()
            },
        )

        if data.username:
            redis_storage.hmset(self.USERNAME_CHAT_ID_KEY, {data.username: data.chat_id})

    def get(self, chat_id: str) -> Optional[UserData]:
        key = self.get_storage_user_prefix(chat_id)
        stored_data = redis_storage.hgetall(key)
        if not stored_data:
            return None
        coordinates = Coordinates(
            float(stored_data[b"latitude"]),
            float(stored_data[b"longitude"])
        )
        user_data = UserData(
            chat_id=chat_id,
            username=stored_data[b"username"].decode("utf-8"),
            coordinates=coordinates,
            updated=datetime.fromisoformat(stored_data[b"updated"].decode("utf-8"))
        )
        return user_data

    def get_by_username(self, username: str) -> Optional[UserData]:
        data = redis_storage.hmget(self.USERNAME_CHAT_ID_KEY, username)
        if not data:
            return None
        chat_id = data[0].decode("utf-8")
        user_data = self.get(chat_id)
        return user_data


class LocationRequestRegistry:

    LOCATION_REQUEST_KEY = "location_requests"
    LOCATION_REQUEST_EXP_TIME = 300

    def get_request_key(self, chat_id_src: str) -> str:
        return f"{self.LOCATION_REQUEST_KEY}_{chat_id_src}"

    def add_location_request(self, chat_id_src: str, chat_id_dst: str):
        key = self.get_request_key(chat_id_src)
        redis_storage.set(key, chat_id_dst, ex=self.LOCATION_REQUEST_EXP_TIME)

    def get_location_request(self, chat_id_src: str) -> Optional[str]:
        key = self.get_request_key(chat_id_src)
        chat_id_dst = redis_storage.get(key)
        if not chat_id_dst:
            return None
        return chat_id_dst.decode("utf-8")


class CityNameToGeoIdMappingStorage:
    """
    Storage class to work with mapping of city names to their geonameids
    """

    MAPPING_KEY = "cities_name_geoid_mapping"

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
location_request_registry = LocationRequestRegistry()
