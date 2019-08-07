import datetime
import json
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse
from django.http.request import QueryDict
from rest_framework import serializers, status as status_code

from auth_system.utils import is_json, set_cookie
from users import repository
from users.constants import SUCCESS, FAIL, LOGIN
from .models import Log


def get_request_data(request):
    if is_json(request.body):
        body = json.loads(request.body)
        query = urlencode(body)
        data = QueryDict(query)
    else:
        data = request.POST
    return data


def set_auth_cookie(res, access_token, refresh_token):
    res = set_cookie(
        response=res,
        key='access_token',
        token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    res = set_cookie(
        response=res,
        key='refresh_token',
        token=refresh_token,
        expires_in=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
    )
    return res


def check_password_is_correct(password, user):
    if not user.check_password(password):
        raise serializers.ValidationError(
            'The current password is not correct!'
        )


def warning_login_failed(user):
    """
    If user failed login 3 times in {settings.LOGIN_TIME_LEVEL_1} minutes, then return True, False (no lock, only captcha)
    If user failed login 5 times in {settings.LOGIN_TIME_LEVEL_2} minutes, then return True, True (lock)
    :param username:
    :return:
    """
    count = 0
    captcha = False
    lock = False
    logs = Log.objects.filter(user=user)
    for log in logs:
        if log.action == LOGIN and log.status == FAIL and in_time(log.timestamp, settings.LOGIN_TIME_LEVEL_2):
            count += 1
            last_log = log
            if not captcha and count == 3 and in_time(last_log.timestamp, settings.LOGIN_TIME_LEVEL_1):
                captcha = True
            if not lock and count == 5 and in_time(last_log.timestamp, settings.LOGIN_TIME_LEVEL_2):
                lock = True
        elif log.action == LOGIN and log.status == SUCCESS:
            break
    if lock:
        return True, True
    elif captcha:
        return True, False
    return False, False


def in_time(time, limit):
    now = datetime.datetime.now(datetime.timezone.utc)
    delta = datetime.timedelta(minutes=limit)
    if time + delta >= now:
        return True
    return False


def get_fail_status(status, user):
    warning, lock = warning_login_failed(user)
    if warning:
        status = status_code.HTTP_423_LOCKED if lock else status_code.HTTP_429_TOO_MANY_REQUESTS
    return status


def account_not_yet_verified(data):
    user = repository.get_user_by_username(username=data['username'])
    if not user:
        unverified_user = repository.get_signup_request_by_username(username=data['username'])
        if unverified_user:
            return HttpResponse(content="Please confirm your account first", status=403)
    return None
