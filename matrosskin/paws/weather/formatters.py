from datetime import datetime
from pyowm.weatherapi25.weather import Weather
from matrosskin.l10n import _


def emodji_condition(condition: str) -> str:
    return {
        "пасмурно": "☁",
        "ясно": "🔆",
        "слегка облачно": "⛅️",
        "легкий дождь": "🌧",
        "облачно": "☁️",
        "clear sky": "🔆",
        "few clouds": "⛅️",
        "broken clouds": "☁",
        "light rain": "🌧",
        "overcast clouds": "☁️",
        "scattered clouds": "🌤️"
    }.get(condition, condition)


class WeatherDayFormatter:

    def __init__(self, temperature: str, wind_speed: str, humidity: str, status: str,
                 pressure: str, ref_time: str, wind_gust: str = ''):
        self.temperature = temperature
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
        self.humidity = humidity
        self.status = status
        self.pressure = pressure
        self.ref_time = ref_time

    @staticmethod
    def create_from_weather_lookup(weather_lookup: Weather):
        wind = weather_lookup.get_wind()
        return WeatherDayFormatter(
            temperature=weather_lookup.get_temperature('celsius').get('temp'),
            wind_speed=wind.get('speed'),
            wind_gust=wind.get('gust', ''),
            humidity=weather_lookup.get_humidity(),
            status=weather_lookup.get_detailed_status(),
            pressure=weather_lookup.get_pressure().get('press'),
            ref_time=weather_lookup.get_reference_time(timeformat='date')
        )

    def get_formatted(self) -> str:
        ref_time_format = '%Y-%m-%d, %H:%M:%S' if isinstance(self.ref_time, datetime) else '%Y-%m-%d'
        values = {
            "ref_time": self.ref_time.strftime(ref_time_format),
            "temperature": self.temperature,
            "condition": emodji_condition(self.status),
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "wind_gusts": self.wind_gust,
            "pressure": self.pressure
        }
        return _("""
- ref time: {ref_time}
- temperature 🌡️ : {temperature}
- condition: {condition}
- humidity: {humidity}
- wind speed  🌬: {wind_speed} mps
- wind gusts: {wind_gusts}
- pressure: {pressure}
        """) . format(**values)


class WeatherForecastFormatter:

    squashable_params = ['temperature', 'wind_speed', 'wind_gust', 'humidity', 'status', 'pressure']

    def __init__(self, city: str, days_list: [Weather], squash_days: bool=True):
        self.city = city
        self.days_list = [WeatherDayFormatter.create_from_weather_lookup(d) for d in days_list]
        if squash_days:
            self.squash_days()

    def squash_days(self) -> None:
        """
        Join weather characteristics for one day
        :return:
        """
        if not self.days_list:
            return

        # gather WeatherDayFormatter's in list by date
        squashed_lists = dict()
        for day in self.days_list:
            day.ref_time = day.ref_time.date()
            squashed_lists[day.ref_time] = squashed_lists.get(day.ref_time, [])
            squashed_lists[day.ref_time].append(day)

        squashed_days = list()
        for forecast_date, hourly_forecast in squashed_lists.items():

            # gather params inside of one day
            day_values = dict()
            for fc in hourly_forecast:
                for param in self.squashable_params:
                    val = getattr(fc, param)
                    if not val:
                        continue
                    val = emodji_condition(val) if param == "status" else str(val)
                    if param not in day_values:
                        day_values[param] = [val]
                    elif day_values[param][-1] != val:
                        day_values[param].append(val)

            day = WeatherDayFormatter(
                **dict((param, ', '.join(values)) for param, values in day_values.items()),
                ref_time=forecast_date
            )
            squashed_days.append(day)

        self.days_list = squashed_days

    def get_formatted(self) -> str:
        phrase = _("Weather for {city}").format(city=self.city)
        formatted_str = f"""
            {phrase}
        
        """
        for day in self.days_list:
            formatted_str += day.get_formatted()

        return formatted_str
