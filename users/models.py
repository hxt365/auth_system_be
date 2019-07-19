import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from async_tasks.tasks import async_send_mail
from .constants import *


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    only_letters = RegexValidator(r'^[A-Za-z]+$', 'Only letters are allowed.')

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, MinLengthValidator(6), ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    password = models.CharField(_('password'), max_length=128, validators=[MinLengthValidator(6)])
    first_name = models.CharField(_('first name'), max_length=30, validators=[only_letters])
    last_name = models.CharField(_('last name'), max_length=30, validators=[only_letters])
    email = models.EmailField(unique=True)

    def send_email(self, message):
        """
        Send email to user via gmail, in order that the user verifies
        his email
        :param
        :return:
        """
        FROM = settings.EMAIL_HOST_USER
        TO = self.email
        res = async_send_mail.delay(FROM, TO, message)
        res.forget()


class SignupRequestManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class SignupRequest(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()
    only_letters = RegexValidator(r'^[A-Za-z]+$', 'Only letters are allowed.')

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, MinLengthValidator(6), ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    password = models.CharField(_('password'), max_length=128, validators=[MinLengthValidator(6)])
    first_name = models.CharField(_('first name'), max_length=30, validators=[only_letters])
    last_name = models.CharField(_('last name'), max_length=30, validators=[only_letters])
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)

    objects = SignupRequestManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def send_email(self, message):
        """
        Send email to user via gmail, in order that the user verifies
        his email
        :param
        :return:
        """
        FROM = settings.EMAIL_HOST_USER
        TO = self.email
        res = async_send_mail.delay(FROM, TO, message)
        res.forget()


class Token(models.Model):
    user = models.OneToOneField(
        SignupRequest,
        on_delete=models.CASCADE,
    )
    token = models.UUIDField(default=uuid.uuid4, )
    timestamp = models.DateTimeField(auto_now_add=True, )

    class Meta:
        verbose_name = 'token'
        verbose_name_plural = 'tokens'

    def __str__(self):
        return str(self.token)


class PasswordsHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passwords'
    )
    content = models.CharField(max_length=100)
    random = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'password'
        verbose_name_plural = 'passwords'

    def __str__(self):
        return self.user.username + ' ' + self.content


class Log(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='logs')
    action = models.CharField(
        max_length=9,
        choices=ACTION
    )
    status = models.CharField(
        max_length=7,
        choices=STATUS,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        ordering = ('-timestamp',)

    def __str__(self):
        return '{username} {action}'.format(
            username=self.user.username,
            action=self.action
        )
