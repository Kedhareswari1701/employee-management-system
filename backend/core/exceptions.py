from pathlib import Path

from decouple import config

from django.core.exceptions import PermissionDenied
from django.core.validators import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404

from rest_framework import exceptions, status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler to produce a consistent JSON error envelope.

    Shape:
        {
            "detail": "...",        # human readable summary
            "errors": [ {...} ]     # optional field-level errors
        }
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(exc.message_dict)

    if isinstance(exc, IntegrityError):
        exc = exceptions.APIException(
            'A database integrity error occurred. The record may already exist or '
            'conflict with existing data.'
        )
        exc.status_code = status.HTTP_409_CONFLICT

    response = exception_handler(exc, context)

    if response is not None:
        data = dict(response.data)
        detail = data.get('detail', 'An error occurred.')
        errors = []
        for field, messages in data.items():
            if field == 'detail':
                continue
            if not isinstance(messages, (list, tuple)):
                messages = [messages]
            for message in messages:
                errors.append({'field': field, 'message': str(message)})

        response.data = {
            'detail': str(detail),
            'errors': errors,
        }

    return response
