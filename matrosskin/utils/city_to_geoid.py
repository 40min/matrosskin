""" utility for maintain mapping of city names to their geoids """

import os
import logging

from modules.storage import city_to_geoid_mapping

SOURCE_FILE_NAME = './matrosskin/utils/cities500.txt'

logger = logging.getLogger(__name__)


def check_and_create_mapping() -> None:
    logger.info('check city to geo mapping ...')
    if not city_to_geoid_mapping.is_mapping_exists():
        logger.info('geo mapping is not exist, try to create it ... ')
        logger.info('this will take a while (over 700k cities in txt file for parsing)')
        if not os.path.isfile(SOURCE_FILE_NAME):
            logger.error('cities500 source file not found in %s', SOURCE_FILE_NAME)
        with open(SOURCE_FILE_NAME, 'r', encoding='utf-8') as cities_source:
            for line in cities_source:
                line_info = line.split('\t')
                if line_info[3]:
                    alternative_names = line_info[3].split(',')
                    for name in alternative_names:
                        if name:
                            city_to_geoid_mapping.add_city(name, line_info[0])
