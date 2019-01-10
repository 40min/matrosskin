from collections import namedtuple

Job = namedtuple('Job', ['callback', 'interval', 'first'])


class Paw:
    name = 'generic paw'
    handlers = set()
    jobs = set()

