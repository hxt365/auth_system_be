from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from oauth2_provider.models import (
    get_access_token_model,
    get_refresh_token_model,
)
from rest_framework import status

from auth_system.utils import set_cookie, random_password
from users.constants import *
from users.signals import signals

USER = get_user_model()
SignupRequest = apps.get_model('users', 'SignupRequest')
Log = apps.get_model('users', 'Log')
Token = apps.get_model('users', 'Token')
Log = apps.get_model('users', 'Log')
PasswordsHistory = apps.get_model('users', 'PasswordsHistory')
AccessTokenModel = get_access_token_model()
RefreshTokenModel = get_refresh_token_model()


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


def clear_tokens(user):
    """
    Clear all tokens used by user, explicit login again
    :param user:
    :return:
    """
    AccessTokenModel.objects.filter(user=user).delete()
    RefreshTokenModel.objects.filter(user=user).delete()


def set_random_password_for_user(user):
    new_password = random_password(user)
    user.set_password(new_password)
    user.save()
    clear_tokens(user)
    PasswordsHistory.objects.create(
        user=user,
        content=user.password,
        random=True,
    )
    return new_password


def set_password_for_user(user, new_password):
    user.set_password(new_password)
    user.save()
    PasswordsHistory.objects.create(
        user=user,
        content=user.password
    )
    clear_tokens(user)


def check_email_token(token):
    """
    If token is valid, return True and token's owner
    :param token:
    :return:
    """
    qs = SignupRequest.objects.filter(token__token=token)
    if qs.exists():
        user = qs.first()
        if user.is_verified:
            return False, None
        return True, user
    return False, None


def verify_email_by_token(token):
    valid, unofficial_user = check_email_token(token)
    if valid:
        unofficial_user.is_verified = True
        unofficial_user.save()
        # Create official user
        user = USER.objects.create(
            username=unofficial_user.username,
            password=unofficial_user.password,
            email=unofficial_user.email,
            first_name=unofficial_user.first_name,
            last_name=unofficial_user.last_name,
        )
        PasswordsHistory.objects.create(
            user=user,
            content=user.password
        )
        SignupRequest.objects.filter(email=user.email).exclude(username=user.username).delete()
    return valid


def send_verification_email_to_user(user, resend=False):
    if resend:
        user.token.delete()
    token = Token(user=user)
    token.save()

    message = """
        From: Teko  company
        To: {}
        http://127.0.0.1:8000/api/auth/email/{}/
    """.format(user.email, token.token)
    user.send_email(message)


def write_log(user, action, status):
    Log.objects.create(
        user=user,
        action=action,
        status=status
    )


def get_user_by_username(username):
    qs = USER.objects.filter(username=username)
    return qs.first()


def send_signal(action, status_code, user=None, username=None):
    if username:
        user = get_user_by_username(username)
    if status.is_success(status_code):
        signals[action].send(sender=user.__class__, user=user, status=SUCCESS)
    else:
        signals[action].send(sender=user.__class__, user=user, status=FAIL)


def login_failed(status_code, username):
    if not status.is_success(status_code):
        fail_logs = Log.objects.filter(user__username=username, action=LOGIN).order_by('-timestamp')
        count = 0
        for log in fail_logs:
            if log.status == FAIL:
                count += 1
            else:
                return
            if count == 5:
                user = get_user_by_username(username)
                user.is_active = FAIL
                user.save()
                return