import redis

from modules.settings import config

pool = redis.ConnectionPool(host=config['host'], port=config['port'], db=config['db'])
redis_storage = redis.Redis(connection_pool=pool)
