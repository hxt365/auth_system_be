from django.dispatch import Signal
from .constants import *


user_logged_in = Signal(providing_args=['user', 'status'])
user_logged_out = Signal(providing_args=['user', 'status'])
user_reset_password = Signal(providing_args=['user', 'status'])
user_changed_password = Signal(providing_args=['user', 'status'])


signals = {
    LOGIN: user_logged_in,
    LOGOUT: user_logged_out,
    CHANGE_PW: user_changed_password,
    RESET_PW: user_reset_password,
}
