from telegram.ext import Updater
import config

updater = Updater(
    token=config.tg_token,
    workers=config.tg_num_workers,
    use_context=True
)
dispatcher = updater.dispatcher
