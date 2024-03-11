import random
import string
from utils.validators import validate_password


def generate_random_password(length=12):
    while True:
        password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
        if validate_password(password):
            return password


async def send_email_user_login_data(email, password, login):
    """Пока временная заглушка. Будем отправлять
    юзеру на почту его данные для логина на его почту"""
    pass
