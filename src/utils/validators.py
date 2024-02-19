import re


def validate_login(login: str) -> bool:
    if not re.match("^[a-zA-Z0-9_-]+$", login):
        return False
    return True


def validate_email(email: str) -> bool:
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False
    return True
