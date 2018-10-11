import importlib
import logging

from bot import dispatcher
from bot import updater

from paws.news import grab_news_callback

logging.basicConfig(format='[%(asctime)s][%(name)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error_callback(bot, update, error):
    pass


def main():
    logger.info('starting...')

    for paw_name in ('weather', 'awesome', 'news', 'owner'):
        module = getattr(importlib.import_module(f'paws.{paw_name}'), 'Paw')
        logger.info('Paw imported: %s (handlers: %d)', module.name, len(module.handlers))
        for handler in module.handlers:
            dispatcher.add_handler(handler)

    dispatcher.add_error_handler(error_callback)

    job_queue = updater.job_queue
    #job_queue.run_repeating(grab_news_callback, interval=60*60*6, first=0)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
