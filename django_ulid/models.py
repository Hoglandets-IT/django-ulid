import ulid
from django.core import exceptions
from django.db import models
from django.utils.translation import gettext_lazy as _
from . import forms

# Helper function so callers don't need to import the ulid package.
def default():
    return ulid.new()

class BaseULIDField(models.Field):
    """
    Base class for handling ULIDs in Django model fields.
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
        return 'CharField' if self.connection.vendor == 'sqlite' else 'UUIDField'

    def db_type(self, connection):
        self.connection = connection
        return 'VARCHAR(26)' if connection.vendor == 'sqlite' else 'UUID'

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, ulid.ULID):
            value = self.to_python(value)
        return str(value) if connection.vendor == 'sqlite' else value.uuid

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


class ULIDField(BaseULIDField, models.Field):
    """
    Django model field type for handling ULIDs.
    This field type is natively stored in the DB as a UUID (when supported) and a string/varchar otherwise.
    """
    pass


class ULIDAutoField(BaseULIDField, models.AutoField):
    """
    An AutoField that uses ULID for unique identifiers.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', default)
        super().__init__(*args, **kwargs)
