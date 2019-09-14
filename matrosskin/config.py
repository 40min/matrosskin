import os
from dotenv import (
    load_dotenv,
    find_dotenv
)

load_dotenv()

# news
data_path = os.getenv("data_path", "./data")
learning_mode = os.getenv("learning_mode", True)

# common settings
owner = os.getenv("owner")

# telegram-api
tg_token = os.getenv("tg_token")
tg_num_workers = os.getenv("tg_num_workers", 32)

# Dropbox
dropbox_token = os.getenv("dropbox_token")

# redis-storage
redis_host = os.getenv("redis_host", "redis")
redis_port = os.getenv("redis_port", 6379)
redis_db = os.getenv("redis_db", 0)

# owm
owm_api_key = os.getenv("owm_api_key")
owm_language = os.getenv("owm_language", "en")

# dialogflow
df_small_talk_project_id = os.getenv("df_small_talk_project_id")
df_weather_project_id = os.getenv("df_weather_project_id")
lang = os.getenv("lang", "ru")

# news
news_filtering = os.getenv("news_filtering", 1)
news_attempts_to_get_filtered = os.getenv("news_attempts_to_get_filtered", 100)
news_learning_mode = os.getenv("news_learning_mode", 0)
