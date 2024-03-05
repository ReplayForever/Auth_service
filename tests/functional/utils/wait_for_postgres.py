# import time
# from sqlalchemy import create_engine
# from sqlalchemy.exc import OperationalError
#
# from utils_config import settings
#
#
# if __name__ == '__main__':
#     engine = create_engine(settings.postgres.url())
#     while True:
#         try:
#             conn = engine.connect()
#             conn.close()
#             break
#         except OperationalError:
#             time.sleep(1)
