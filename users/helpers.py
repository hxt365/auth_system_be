import json

from django.conf import settings
from rest_framework import status

from auth_system.utils import is_json, set_cookie
from users.constants import SUCCESS, FAIL
from users.repository import get_user_by_username
from users.signals import signals
from django.http.request import QueryDict
from urllib.parse import urlencode


def get_request_data(request):
    if is_json(request.body):
        body = json.loads(request.body)
        query = urlencode(body)
        data = QueryDict(query)
    else:
        data = request.POST
    return data


def send_signal(action, status_code, user=None, username=None):
    if not user and not username:
        return
    if username:
        user = get_user_by_username(username)
    if status.is_success(status_code):
        signals[action].send(sender=user.__class__, user=user, status=SUCCESS)
    else:
        signals[action].send(sender=user.__class__, user=user, status=FAIL)


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