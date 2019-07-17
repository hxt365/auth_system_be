from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _
from rest_framework import status


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Bad request (400)')
    default_code = 'badrequest'