import datetime

from pyowm.weatherapi25.weather import Weather


class WeatherDay:

    def __init__(self, temperature: str, wind_speed: str, wind_gust: str, humidity: str, status: str,
                 pressure:str, ref_time: str):
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
        return WeatherDay(
            temperature=weather_lookup.get_temperature('celsius').get('temp'),
            wind_speed=wind.get('speed'),
            wind_gust=wind.get('gust'),
            humidity=weather_lookup.get_humidity(),
            status=weather_lookup.get_detailed_status(),
            pressure=weather_lookup.get_pressure().get('press'),
            ref_time=weather_lookup.get_reference_time(timeformat='iso')
        )

    def merge_from_day(self, day):
        self.temperature += f', {day.temperature}'
        self.wind_speed += f', {day.wind_speed}'
        self.wind_gust += f', {day.wind_gust}'
        self.humidity += f', {day.humidity}'
        self.status += f', {day.status}'
        self.pressure += f', {day.pressure}'
        self.ref_time += day.ref_time

    def get_formatted(self) -> str:
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

    def __init__(self, city: str, days_list: [Weather], squash_days: bool=True):
        self.city = city
        self.days_list = [WeatherDay.create_from_weather_lookup(d) for d in days_list]
        if squash_days:
            self.squash_days()

    def squash_days(self) -> None:
        squashed_days = list()
        current_day = None
        for day in self.days_list:
            # stopping here on converting
            #
            # todo:
            # finish this forecast squash
            # check regular weather
            # refactor weather and forecast to classes
            # add forecast with dialogflow integration
            # add forecast by city
            # refactore 'approve' button

            d_date = datetime.date.fromtimestamp(day.ref_time)
            if not current_day or d_date != current_day.ref_time:
                if current_day:
                    squashed_days.append(current_day)
                current_day = day
                current_day.ref_time = d_date
            else:
                current_day.merge_from_day(day)
        self.days_list = squashed_days

    def get_formatted(self) -> str:
        formatted_str = f"""
            Weather for {self.city}
        
        """
        for day in self.days_list:
            formatted_str += day.get_formatted_weather(d)

        return formatted_str
