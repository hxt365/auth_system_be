from rest_framework import serializers
from . import repository

from auth_system.utils import check_if_new_password_valid
from users.models import User


def validate_email_is_already_used(email):
    already_in = User.objects.filter(email=email).exists()
    if already_in:
        raise serializers.ValidationError(
            'The email is already used'
        )


def validate_passwords_match(password_1, password_2):
    if password_1 != password_2:
        raise serializers.ValidationError(
            'Passwords are not matched'
        )


def validate_username_and_email_are_already_used(email, username):
    exist = User.objects.filter(username=username, email=email) \
        .exists()
    if not exist:
        raise serializers.ValidationError(
            'The username or email is not correct'
        )


def validate_password_differs_from_5_lastest(password, user):
    if not check_if_new_password_valid(user, password):
        raise serializers.ValidationError(
            'Your new password must be different from the 5 latest \
            passwords!'
        )

def validate_username_is_already_used(username):
    user = repository.get_user_by_username(username)
    if user:
        raise serializers.ValidationError(
            'Username was taken'
        )
