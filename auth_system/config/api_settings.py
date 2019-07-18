REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
}

# CORS settings

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CORS_ALLOW_CREDENTIALS = True


# Oauth2 settings

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend'
)

ACCESS_TOKEN_EXPIRE_SECONDS = 1800
REFRESH_TOKEN_EXPIRE_SECONDS = 1800

CLIENT_ID = 'ScI9WdcmNJTWQhA0QB1Yy2JFIpx4kEeUOlhwHXIc'
CLIENT_SECRET = 'IKd6dpqHj8Q1nuKF6SqXm7CPmRnRi8aMZafxq3u37DiV8vcGCwLoAjzt1Qr73MOY' \
                'm0AQvBPhmN540qOBn2D32zpQrrKN8tfuSAy3OIbtpXhablNsIUfFExGDxMcnsHhW'

API_LOGIN = 'http://127.0.0.1:8000/o/token/'
API_REGISTER = 'http://127.0.0.1:8000/o/token/'
API_REFRESH = 'http://127.0.0.1:8000/o/token/'
