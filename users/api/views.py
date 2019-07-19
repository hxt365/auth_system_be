import json

from braces.views import CsrfExemptMixin
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from oauth2_provider.views.base import TokenView
from rest_framework import views, generics, permissions
from rest_framework.exceptions import ValidationError

from users import services, helpers
from users.services import account_not_yet_verified
from .serializers import (
    LoginSerializer,
    SignUpSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from ..models import SignupRequest

USER = get_user_model()


class LoginApiView(CsrfExemptMixin, TokenView):
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        data = helpers.get_request_data(request)
        serializer = LoginSerializer(data=data)
        try:
            if serializer.is_valid(raise_exception=True):
                return \
                    account_not_yet_verified(data) \
                    or self.login(request=request, data=serializer.validated_data)
        except ValidationError as e:
            msg = json.dumps(e.detail)
            return HttpResponse(content=msg, status=400)

    def login(self, request, data):
        request = services.config_login_request(
            request=request,
            username=data['username'],
            password=data['password'])
        print(request.POST)
        url, headers, body, status = self.create_token_response(request)
        return services.create_auth_response(body, headers, status, data)


class RefreshApiView(CsrfExemptMixin, TokenView):
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        request = services.config_refresh_request(request)
        url, headers, body, status = self.create_token_response(request)
        return services.create_auth_response(body, headers, status)


class SignUpApiView(CsrfExemptMixin, generics.CreateAPIView):
    """
    Register view
    Only POST
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer
    queryset = SignupRequest.objects.all()


class ResetPasswordAPIView(CsrfExemptMixin, views.APIView):
    """
    Send user a new password
    Only POST
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return services.reset_password(data=serializer.validated_data)


class ChangePasswordAPIView(views.APIView):
    """
    Change password
    Only POST
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = ChangePasswordSerializer
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'user': self.request.user,
        }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            return services.change_password(
                new_password=data['new_pass'],
                user=request.user
            )


class LogoutAPIView(views.APIView):
    """
    Log user out
    Only POST
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return services.logout(user=request.user)


class VerifyEmailAPIView(views.APIView):
    """
    Resend code or verify code
    Only GET
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        return services.verify_email(token)
