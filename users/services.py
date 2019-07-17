import json

import requests
from django.conf import settings
from rest_framework.response import Response
from .helpers import get_user_by_username
from auth_system.utils import get_from_cookies_by_name
from users.api.serializers import LoginSerializer
from users.constants import *
from users.helpers import send_signal, verify_email_by_token, set_auth_cookie, \
    set_random_password_for_user, set_password_for_user, clear_tokens


def login(data):
    res = None
    serializer = LoginSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        body = {
            'grant_type': 'password',
            'username': data['username'],
            'password': data['password'],
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
        }
        res = requests.post(
            url=settings.API_LOGIN,
            data=body,
        )
    res = auth_response_successful_or_fail(
        response=res,
        fail_response=Response(
            data='Username / password is not correct',
            status=400),
        msg='Logged in successfully'
    )
    send_signal(action=LOGIN, status_code=res.status_code, username=data['username'])
    # login_failed(status_code=res.status_code, username=data['username'])
    return res


def refresh(request):
    token = get_from_cookies_by_name(
        cookies=request.COOKIES,
        name='refresh_token'
    )
    if not token:
        return Response(data='Refresh_token expired', status=400)
    body = {
        'grant_type': 'refresh_token',
        'refresh_token': token,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
    }
    res = requests.post(
        url=settings.API_REFRESH,
        data=body,
    )
    res = auth_response_successful_or_fail(
        response=res,
        fail_response=Response(
            data='Refresh_token is not correct or expired',
            status=400),
        msg='Refreshed successfully'
    )
    return res


def verify_email(token):
    valid = verify_email_by_token(token)
    if valid:
        return Response(
            data="Successfully verified",
            status=200,
        )
    else:
        return Response(
            data="Invalid token",
            status=400,
        )


def auth_response_successful_or_fail(response, fail_response, msg=None):
    content = json.loads(response.content.decode())
    try:
        access_token = content['access_token']
        refresh_token = content['refresh_token']
    except KeyError:
        return fail_response
    response = Response(data=msg, status=200)
    response = set_auth_cookie(response, access_token, refresh_token)
    return response


def reset_password(data):
    user = get_user_by_username(username=data['username'])
    new_password = set_random_password_for_user(user)
    # Send email to user
    message = """
            From: Teko
            To: {}
            New password: {}""".format(user.email, new_password)
    user.send_email(message)
    send_signal(action=RESET_PW, status_code=200, user=user)
    return Response(data='Resetted password', status=200)


def change_password(new_password, user):
    set_password_for_user(
        user=user,
        new_password=new_password,
    )
    send_signal(action=CHANGE_PW, status_code=200, user=user)
    return Response(data='Changed password', status=200)


def logout(user):
    clear_tokens(user)
    send_signal(action=LOGOUT, status_code=200, user=user)
    return Response(data='Logged out successfully', status=200)