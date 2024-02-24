import re


def validate_login(login: str) -> bool:
    if not re.match("^[a-zA-Z0-9_-]+$", login):
        return False
    if len(login) < 6 or (len(login) > 255):
        return False
    return True


def validate_email(email: str) -> bool:
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False
    return True


def validate_password(password: str) -> bool:
    if not re.match(r"^(?!.*(.)\1\1)(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{8,}$", password):
        return False
    return True
