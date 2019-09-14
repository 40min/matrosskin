from abc import (
    ABC,
    abstractmethod
)

import pyowm
from pyowm.weatherapi25.observation import Observation
from pyowm.exceptions.api_response_error import NotFoundError


import config
from modules.storage import (
    Coordinates,
    city_to_geoid_mapping
)
from .formatters import (
    WeatherDayFormatter,
    WeatherForecastFormatter
)

owm = pyowm.OWM(API_key=config.owm_api_key, language=config.owm_language)

WEATHER_NOT_FOUND_MESSAGE = 'weather not found'


class Forecast(ABC):
    """ Abstract forecast class"""

    @abstractmethod
    def get_by_city(self, city: str) -> str:
        pass

    @abstractmethod
    def get_by_coords(self, coords: Coordinates) -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_as_txt(observation: Observation, location_name: str) -> str:
        pass


class DayForecast(Forecast):
    """ Provides forecast for one day """

    def get_by_city(self, city: str) -> str:
        try:
            observation = owm.weather_at_place(city)
        except NotFoundError:
            city_from_local_mapping = city_to_geoid_mapping.get_city_geoid(city)
            if not city_from_local_mapping:
                return WEATHER_NOT_FOUND_MESSAGE

            observation = owm.weather_at_id(city_from_local_mapping)

        weather_txt = self.get_as_txt(observation, location_name=city)
        return weather_txt

    def get_by_coords(self, coords: Coordinates) -> str:
        try:
            observation = owm.weather_at_coords(lat=coords.latitude, lon=coords.longitude)
            location = observation.get_location()
            location_txt = f'{location.get_country()} - {location.get_name()}'
        except NotFoundError:
            return WEATHER_NOT_FOUND_MESSAGE

        weather_txt = self.get_as_txt(observation, location_txt)
        return weather_txt

    @staticmethod
    def get_as_txt(observation: Observation, location_name: str) -> str:
        weather_lookup = observation.get_weather()
        day = WeatherDayFormatter.create_from_weather_lookup(weather_lookup)

        weather_txt = f"""
            Weather for location {location_name}
            {day.get_formatted()}
            """

        return weather_txt


class MultipleDaysForecast(Forecast):
    """ Provides forecast for multiple days """

    def get_by_coords(self, coords: Coordinates) -> str:
        forecaster = owm.three_hours_forecast_at_coords(lat=coords.latitude, lon=coords.longitude)
        if not forecaster:
            return WEATHER_NOT_FOUND_MESSAGE

        weathers = forecaster.get_forecast().get_weathers()
        location = forecaster.get_forecast().get_location()
        location_txt = f'{location.get_country()} - {location.get_name()}'
        weather_txt = self.get_as_txt(weathers, location_txt)

        return weather_txt

    def get_by_city(self, city: str) -> str:
        try:
            forecaster = owm.three_hours_forecast(name=city)
        except NotFoundError:
            geoid = city_to_geoid_mapping.get_city_geoid(city)
            if not geoid:
                return WEATHER_NOT_FOUND_MESSAGE
            forecaster = owm.three_hours_forecast_at_id(geoid)

        weathers = forecaster.get_forecast().get_weathers()
        weather_txt = self.get_as_txt(weathers, location_name=city)

        return weather_txt

    @staticmethod
    def get_as_txt(observations, location_name: str) -> str:
        forecast = WeatherForecastFormatter(location_name, observations)
        weather_txt = f"""
                    {forecast.get_formatted()}
                    """
        return weather_txt


day_forecast = DayForecast()
multiple_days_forecast = MultipleDaysForecast()
