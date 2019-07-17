from rest_framework import serializers
from validate_email import validate_email

from auth_system.utils import check_if_new_password_valid
from ..models import SignupRequest, PasswordsHistory, User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )


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
        already_in = SignupRequest.objects.filter(username=username)\
            .exists()
        if already_in:
            raise serializers.ValidationError(
                'The username is already used'
            )
        return username

    def validate_email(self, email):
        # Validate email
        if not validate_email(email):
            raise serializers.ValidationError('The email is not valid')
        # Check if email is already used
        already_in = User.objects.filter(email=email).exists()
        if already_in:
            raise serializers.ValidationError(
                'The email is already used'
            )
        return email

    def validate(self, data):
        password_1 = data['password']
        password_2 = data['password_2']
        if password_1 != password_2:
            raise serializers.ValidationError(
                'Passwords are not matched'
            )
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


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )
    new_pass = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )
    new_pass_2 = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,
    )

    def validate(self, data):
        old_pass = data['old_pass']
        new_pass = data['new_pass']
        new_pass_2 = data['new_pass_2']
        # Check new_pass and new_pass_2
        if new_pass != new_pass_2:
            raise serializers.ValidationError(
                'New passwords do not match each other'
            )
        # Get user from context, passed from get_serializer_context
        user = self.context['user']
        # Check if the password is correct
        if not user.check_password(old_pass):
            raise serializers.ValidationError(
                'The old password is not correct'
            )
        # Check if the new password is different from 5 latest passwords
        if not check_if_new_password_valid(user, new_pass):
            raise serializers.ValidationError(
                'Your new password must be different from the 5 latest \
                passwords'
            )
        return data


class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True,)
    email = serializers.CharField(max_length=150, required=True,)

    def validate(self, data):
        username = data['username']
        email = data['email']
        # Validate email
        if not validate_email(email):
            raise serializers.ValidationError('The email is not valid')
        # Check if account contains that username and email exists
        exist = User.objects.filter(username=username, email=email)\
            .exists()
        if not exist:
            raise serializers.ValidationError(
                'The username or email is not correct'
            )
        return data

