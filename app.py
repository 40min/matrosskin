import importlib
import logging

from bot import dispatcher
from bot import updater

logging.basicConfig(format='[%(asctime)s][%(name)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error_callback(bot, update, error):
    pass


def main():
    logger.info('starting...')

    for paw_name in ('weather', 'awesome', 'news'):
        module = getattr(importlib.import_module(f'paws.{paw_name}'), 'Paw')
        logger.info('Paw imported: %s (handlers: %d)', module.name, len(module.handlers))
        for handler in module.handlers:
            dispatcher.add_handler(handler)

    dispatcher.add_error_handler(error_callback)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
