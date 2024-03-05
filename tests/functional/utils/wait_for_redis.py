# import time
#
# from redis import Redis
#
# from utils_config import settings
#
#
# if __name__ == '__main__':
#     redis_client = Redis(host=settings.redis.host, port=settings.redis.port)
#     while True:
#         if redis_client.ping():
#             break
#         time.sleep(1)
