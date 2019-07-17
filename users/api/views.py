from braces.views import CsrfExemptMixin
from django.contrib.auth import get_user_model
from rest_framework import views, generics, permissions

from users import services
from .serializers import (
    SignUpSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from ..models import SignupRequest

USER = get_user_model()


class LoginApiView(CsrfExemptMixin, views.APIView):
    """
    Login view
    Only POST
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        res = services.login(data=request.data)
        return res


class RefreshApiView(CsrfExemptMixin, views.APIView):
    """
    Refresh token for user
    Only POST
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        res = services.refresh(request=request)
        return res


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
