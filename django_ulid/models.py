"""
    django_ulid/models
    ~~~~~~~~~~~~~~~~~~

    Contains functionality for Django model support.
"""
import ulid
from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _  # Using gettext_lazy for better lazy translation
from . import forms
from django.db.models import AutoFieldMixin
 
# Helper function so callers don't need to import the ulid package.
def default():
    return ulid.new()

class ULIDField(models.Field):
    """
    Django model field type for handling ULID's.

    This field type is natively stored in the DB as a UUID (when supported) and a string/varchar otherwise.
    """
    description = _('Universally Unique Lexicographically Sortable Identifier')
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, **kwargs):
        kwargs.setdefault('max_length', 26)
        super().__init__(verbose_name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'UUIDField'

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, ulid.ULID):
            value = self.to_python(value)
        return value.uuid if connection.features.has_native_uuid_field else str(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, ulid.ULID):
            return value
        try:
            return ulid.from_str(value)
        except (AttributeError, ValueError):
            raise exceptions.ValidationError(
                _("'%(value)s' is not a valid ULID."),
                code='invalid',
                params={'value': value}
            )

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.ULIDField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

class ULIDAutoField(AutoFieldMixin, ULIDField):
    """
    An AutoField that uses ULID for unique identifiers.
    """
    def get_internal_type(self):
        return "ULIDAutoField"

    def rel_db_type(self, connection):
        return ULIDField().db_type(connection=connection)
