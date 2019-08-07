import json

import requests
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework import status as status_code
from rest_framework.response import Response
from decouple import config
import users.repository
from auth_system.utils import get_from_cookies_by_name
from auth_system.utils import is_UUID
from users import helpers, repository
from users.api.serializers import UserSerializer
from users.constants import *
from users.helpers import get_fail_status
from .repository import get_user_by_username, lock_user


def verify_email(token):
    if not is_UUID(token):
        return Response(
            data="Invalid token",
            status=400,
        )
    valid, expired = repository.verify_email_by_token(token)
    if valid:
        return Response(
            data="Successfully verified",
            status=200,
        )
    elif expired:
        return Response(
            data="Token expired",
            status=400,
        )
    else:
        return Response(
            data="Invalid token",
            status=400,
        )


def reset_password(data):
    user = get_user_by_username(username=data['username'])
    new_password = repository.set_random_password_for_user(user)
    # Send email to user
    message = """
            From: Teko
            To: {}
            New password: {}""".format(user.email, new_password)
    user.send_email(message)
    users.repository.send_signal(action=RESET_PW, status_code=200, user=user)
    return Response(data='Resetted password', status=200)


def change_password(new_password, user):
    repository.set_password_for_user(
        user=user,
        new_password=new_password,
    )
    users.repository.send_signal(action=CHANGE_PW, status_code=200, user=user)
    return Response(data='Changed password', status=200)


def logout(user):
    repository.clear_tokens(user)
    users.repository.send_signal(action=LOGOUT, status_code=200, user=user)
    return Response(data='Logged out successfully', status=200)


def config_login_request(request, username, password):
    request.POST = request.POST.copy()
    request.POST['username'] = username
    request.POST['password'] = password
    request.POST['grant_type'] = 'password'
    request.POST['client_id'] = settings.CLIENT_ID
    request.POST['client_secret'] = settings.CLIENT_SECRET
    return request


def config_refresh_request(request):
    token = get_from_cookies_by_name(request.COOKIES, 'refresh_token')

    request.POST = request.POST.copy()
    request.POST['grant_type'] = 'refresh_token'
    request.POST['refresh_token'] = token
    request.POST['client_id'] = settings.CLIENT_ID
    request.POST['client_secret'] = settings.CLIENT_SECRET
    return request


def create_auth_response(body, headers, status, data={}):
    if not check_captcha(data):
        body = "Captcha is not correct!"
        status = status_code.HTTP_400_BAD_REQUEST
    if status == status_code.HTTP_200_OK:
        loaded_body = json.loads(body)
        access_token = loaded_body.get('access_token')
        refresh_token = loaded_body.get('refresh_token')
        user = repository.get_user_by_access_token(access_token)
        payload = json.dumps(UserSerializer(user).data)
        response = HttpResponse(content=payload, status=status)
        response = helpers.set_auth_cookie(response, access_token, refresh_token)
        users.repository.send_signal(action=LOGIN, status_code=status, user=user)
    else:
        username = data.get('username')
        user = get_user_by_username(username)
        body = "Password or username is not correct!"
        if user:
            users.repository.send_signal(action=LOGIN, status_code=status, username=username)
            status = get_fail_status(status, user)
            lock_or_catpcha(status, user, username)
        response = HttpResponse(content=body, status=status)

    for k, v in headers.items():
        response[k] = v
    return response


def check_captcha(data):
    username = data.get('username')
    if username:
        user_status = cache.get(username)
        if user_status == 'CAPTCHA':
            res = requests.post(
                url='https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': config('RECAPTCHA_KEY'),
                    'response': data.get('captcha'),
                }, );
            content = json.loads(res.content)
            return content['success']
    return True


def lock_or_catpcha(status, user, username):
    if status == status_code.HTTP_423_LOCKED:
        lock_user(user)
        cache.set(username, 'LOCKED', settings.CACHE_TTL)
    elif status == status_code.HTTP_429_TOO_MANY_REQUESTS:
        cache.set(username, 'CAPTCHA', 60*5)
