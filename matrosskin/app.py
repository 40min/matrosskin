import logging

from bot import dispatcher
from bot import updater

from matrosskin.paws import get_my_paws
from matrosskin.utils.city_to_geoid import check_and_create_mapping

logging.basicConfig(format='[%(asctime)s][%(name)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error_callback(bot, update, error):
    pass


def main():
    logger.info('starting...')
    check_and_create_mapping()

    job_queue = updater.job_queue
    for paw in get_my_paws():
        logger.info('Paw imported: %s (handlers: %d)', paw.name, len(paw.handlers))
        for handler in paw.handlers:
            dispatcher.add_handler(handler)
        for job in paw.jobs:
            job_queue.run_repeating(*job)

    dispatcher.add_error_handler(error_callback)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
