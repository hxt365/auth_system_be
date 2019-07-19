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

CLIENT_ID = 'owlFtMLr96BO4LAuBEvP0FWS79T8pPZUwO2jCzRn'
CLIENT_SECRET = 'dE5WJu75vAtN2SiudlM0DEKqiuOrIwPl24mpogU3ZXYp8XnEZEZwSoNjkRplma' \
                'i2xv5EtzTLuoUfi1qS2YQyqODOK7yUsiP5WXIT334ZYjdD2ZdIJtNaZWcizH5R7Mzy'

API_LOGIN = 'http://127.0.0.1:8000/o/token/'
API_REGISTER = 'http://127.0.0.1:8000/o/token/'
API_REFRESH = 'http://127.0.0.1:8000/o/token/'
