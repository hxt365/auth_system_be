from django.contrib import admin
from .models import (
    Token,
    User,
    SignupRequest,
    PasswordsHistory,
    Log,
)

class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'status')

    class Meta:
        model = Log

admin.site.register(User)
admin.site.register(SignupRequest)
admin.site.register(Token)
admin.site.register(PasswordsHistory)
admin.site.register(Log, LogAdmin)
