from django.contrib import admin
from .models import (
    Token,
    User,
    SignupRequest,
    PasswordsHistory,
    Log,
)

admin.site.register(User)
admin.site.register(SignupRequest)
admin.site.register(Token)
admin.site.register(PasswordsHistory)
admin.site.register(Log)
