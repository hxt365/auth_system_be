from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import SignupRequest
from .repository import send_verification_email_to_user, write_log
from .signals import *


@receiver(post_save, sender=SignupRequest)
def send_verification_email(sender, instance, created, **kwargs):
    if created:
        send_verification_email_to_user(instance)


@receiver(user_logged_in)
def user_logged_in_handler(user=None, status=None, **kwargs):
    if status == SUCCESS:
        cache.delete(user.username)
    write_log(user=user, action=LOGIN, status=status)


@receiver(user_logged_out)
def user_logged_out_handler(user=None, status=None, **kwargs):
    # print('USER LOGGED OUT')
    write_log(user=user, action=LOGOUT, status=SUCCESS)


@receiver(user_reset_password)
def user_reset_password_handler(user=None, status=None, **kwargs):
    # print('USER RESET PASSWORD')
    write_log(user=user, action=RESET_PW, status=SUCCESS)


@receiver(user_changed_password)
def user_changed_password_handler(user=None, status=None, **kwargs):
    # print('USER CHANGED PASSWORD')
    write_log(user=user, action=CHANGE_PW, status=SUCCESS)
