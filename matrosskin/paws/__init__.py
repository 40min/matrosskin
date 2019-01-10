from .awesome import AwesomePaw
from .news import NewsPaw
from .owner import OwnerPaw
from .weather import WeatherPaw


def get_my_paws():
    return [
        AwesomePaw(),
        NewsPaw(),
        OwnerPaw(),
        WeatherPaw(),
    ]
