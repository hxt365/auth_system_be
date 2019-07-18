import json

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status as status_code
from rest_framework.response import Response

from auth_system.utils import get_from_cookies_by_name
from auth_system.utils import is_UUID
from users.api.serializers import UserSerializer
from users.constants import *
from users.helpers import send_signal, set_auth_cookie
from users.repository import verify_email_by_token, set_random_password_for_user, set_password_for_user, clear_tokens, \
    get_user_by_access_token
from .repository import get_user_by_username


def verify_email(token):
    if not is_UUID(token):
        return Response(
            data="Invalid token",
            status=400,
        )
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
    response = HttpResponse(content=body, status=status)
    if status == status_code.HTTP_200_OK:
        loaded_body = json.loads(body)
        access_token = loaded_body.get('access_token')
        refresh_token = loaded_body.get('refresh_token')
        user = get_user_by_access_token(access_token)
        payload = json.dumps(UserSerializer(user).data)
        response = HttpResponse(content=payload, status=status)
        response = set_auth_cookie(response, access_token, refresh_token)
        send_signal(action=LOGIN, status_code=status, user=user)
    else:
        send_signal(action=LOGIN, status_code=status, username=data.get('username'))
        # login_failed(status_code=res.status_code, username=data['username'])

    for k, v in headers.items():
        response[k] = v
    return response


