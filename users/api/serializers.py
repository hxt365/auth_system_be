from rest_framework import serializers

from users.helpers import check_password_is_correct
from users import validators
from users.validators import validate_password_differs_from_5_lastest
from ..models import SignupRequest, User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )
    captcha = serializers.CharField(max_length=350)


class SignUpSerializer(serializers.ModelSerializer):
    password_2 = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )

    class Meta:
        model = SignupRequest
        fields = (
            'username', 'first_name',
            'last_name', 'password',
            'password_2', 'email')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, username):
        validators.validate_username_is_already_used(username)
        return username

    def validate_email(self, email):
        validators.validate_email_is_already_used(email)
        return email

    def validate(self, data):
        validators.validate_passwords_match(
            password_1=data['password'],
            password_2=data['password_2'])
        return data

    def create(self, validated_data):
        user = SignupRequest.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'first_name',
            'last_name', 'email')


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(
        max_length=150,
        min_length=6,
        required=True,
        write_only=True,
    )
    new_pass = serializers.CharField(
        max_length=150,
        min_length=6,
        required=True,
        write_only=True,
    )
    new_pass_2 = serializers.CharField(
        max_length=150,
        min_length=6,
        required=True,
        write_only=True,
    )

    def validate(self, data):
        old_pass = data['old_pass']
        new_pass = data['new_pass']
        new_pass_2 = data['new_pass_2']
        validators.validate_passwords_match(password_1=new_pass, password_2=new_pass_2)
        user = self.context['user']
        check_password_is_correct(old_pass, user)
        validate_password_differs_from_5_lastest(new_pass, user)
        return data


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True, )
    email = serializers.CharField(max_length=150, required=True, )

    def validate(self, data):
        username = data['username']
        email = data['email']
        validators.validate_username_and_email_are_already_used(email, username)
        return data
