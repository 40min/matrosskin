from collections import namedtuple

Coordinates = namedtuple('Coordinates', ['latitude', 'longitude'])


class WeatherDay:

    def __init__(self, weather_lookup):
        self.temperature = weather_lookup.get_temperature('celsius').get('temp')
        wind = weather_lookup.get_wind()
        self.wind_speed = wind.get('speed')
        self.wind_gust = wind.get('gust')
        self.humidity = weather_lookup.get_humidity()
        self.status = weather_lookup.get_detailed_status()
        self.pressure = weather_lookup.get_pressure().get('press')
        self.ref_time = weather_lookup.get_reference_time(timeformat='iso')

    def get_formatted(self):
        return f"""
- temperature: {self.temperature}
- condition: {self.status}
- humidity: {self.humidity}
- wind speed: {self.wind_speed}
- wind gusts: {self.wind_gust}
- pressure: {self.pressure}
- ref time: {self.ref_time}
        """


class WeatherForecast:

    def __init__(self, city, days_list=None):
        self.city = city
        self.days_list = days_list if days_list else []

    def get_formatted(self):
        formatted_str = f"""
            Weather for {self.city}
        
        """
        for d in self.days_list:
            formatted_str += d.get_formatted()

        return formatted_str
