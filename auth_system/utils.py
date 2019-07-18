import json
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.hashers import (
    check_password, )


def set_cookie(response, key, token, expires_in):
    expires = datetime.utcnow() + timedelta(seconds=int(expires_in))
    response.set_cookie(
        key=key,
        value=token,
        expires=expires,
        httponly=True
    )
    return response


def check_if_new_password_valid(user, new_password):
    """
    If the new_password is one of 5 latest passwords, so return False,
    else return True
    :param user:
    :param new_password:
    :return:
    """
    # hashed_new_password = make_password(new_password)
    password_list = user.passwords.all().order_by('-timestamp')[:5]
    for pw in password_list:
        if check_password(new_password, pw.content):
            return False
    return True


def random_password(user):
    """
    Create a new random password
    :param user:
    :return:
    """
    new_password = str(uuid.uuid4())[:10].replace('-', 'x')
    while not check_if_new_password_valid(user, new_password):
        new_password = str(uuid.uuid4())[:10].replace('-', 'x')
    return new_password


def str_to_dict(string):
    """
    Convert a string like "abc=xyz;def=uvt" to a dict
    :param string:
    :return: dict
    """
    strings_by_semicolon = string.split('; ')
    strings = [string.split('=', 1) for string in strings_by_semicolon]
    result = {k: v for [k, v] in strings}
    return result


def get_from_cookies_by_name(cookies, name):
    token = None
    try:
        token = cookies[name]
    except KeyError:
        pass
    finally:
        return token


def is_json(data):
    try:
        json.loads(data)
    except:
        return False
    return True

def is_UUID(token):
    try:
        token = uuid.UUID(token)
    except:
        return False
    return True