import re


def sanitize_for_redis(txt: str) -> str:
    return re.sub("'|\"|;|,|&", "", txt)
