from django.urls import path
from .views import (
    LoginApiView,
    RefreshApiView,
    SignUpApiView,
    ChangePasswordAPIView,
    ResetPasswordAPIView,
    LogoutAPIView,
    VerifyEmailAPIView,
)

app_name = 'api_auth'

urlpatterns = [
    path('refresh/', RefreshApiView.as_view(), name='refresh'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('signup/', SignUpApiView.as_view(), name='signup'),
    path('password/change/', ChangePasswordAPIView.as_view(), name='change_password'),
    path('password/reset/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('email/<token>/', VerifyEmailAPIView.as_view(), name='email'),
]