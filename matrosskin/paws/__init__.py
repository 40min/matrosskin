from matrosskin.paws.awesome import AwesomePaw
from matrosskin.paws.news import NewsPaw
from matrosskin.paws.owner import OwnerPaw
from matrosskin.paws.weather.paw import WeatherPaw
from matrosskin.paws.talks.paw import TalksPaw
from matrosskin.paws.friend_finder import FriendFinderPaw
from matrosskin.paws.corona.paw import CoronaPaw


def get_my_paws():
    return [
        AwesomePaw(),
        NewsPaw(),
        OwnerPaw(),
        WeatherPaw(),
        TalksPaw(),
        FriendFinderPaw(),
        CoronaPaw()
    ]
