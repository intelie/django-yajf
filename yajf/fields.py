# -*- coding: utf-8 -*-
import functools
import copy
import json
import inspect
from decimal import Decimal

import django
from django.db import models
from django.utils import six

from .encoder import JSONEncoder


__all__ = ['JSONField', 'DecimalJSONField']


if django.VERSION[:2] < (1, 8):
    from django.db.models import SubfieldBase
    field_class = functools.partial(six.with_metaclass, SubfieldBase)
else:
    field_class = functools.partial(six.with_metaclass, type)


class JSONField(field_class(models.Field)):
    MUST_CHECK_STACK = django.VERSION < (1, 8)
    JSON_MODULE = json
    LOAD_KWARGS = {}
    DUMP_KWARGS = {
        'cls': JSONEncoder,
        'separators': (',', ':')
    }

    def __init__(self, *args, **kwargs):
        if 'json_module' in kwargs:
            self.JSON_MODULE = kwargs.pop('json_module')
        if 'load_kwargs' in kwargs:
            self.LOAD_KWARGS = kwargs.pop('load_kwargs')
        if 'dump_kwargs' in kwargs:
            self.DUMP_KWARGS = kwargs.pop('dump_kwargs')

        super(JSONField, self).__init__(*args, **kwargs)

    @classmethod
    def loads(cls, dumped_obj, **kwargs):
        """
        Calls cls.JSON_MODULE.loads with kwargs or cls.LOAD_KWARGS
        """

        if not kwargs:
            kwargs = cls.LOAD_KWARGS

        return cls.JSON_MODULE.loads(dumped_obj, **kwargs)

    @classmethod
    def dumps(cls, obj, **kwargs):
        """
        Calls cls.JSON_MODULE.dumps with kwargs or cls.DUMP_KWARGS
        """

        if not kwargs:
            kwargs = cls.DUMP_KWARGS

        return cls.JSON_MODULE.dumps(obj, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        """Django<1.8 only; tries to infer
        if value was retrieved from db and, if so,
        converts it to a Python object"""

        if self.MUST_CHECK_STACK:
            stack = inspect.stack()
            retrieved_from_db = any(t[3] == '_fetch_all' for t in stack)

            if retrieved_from_db:
                return self.from_db_value(value)

        return value

    def from_db_value(self, value, *args, **kwargs):
        """Django 1.8 only, converts a JSON string to a Python object"""

        return self.loads(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if value is None and self.null:
            return None

        if isinstance(value, bytes):
            value = value.decode('utf-8')

        value = self.dumps(value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)

    def value_from_object(self, obj):
        value = super(JSONField, self).value_from_object(obj)
        if self.null and value is None:
            return None
        return self.dumps_for_display(obj)

    def dumps_for_display(self, value):
        return self.dumps(value)

    def get_default(self):
        """
        Returns the default value for this field.
        The default implementation on models.Field calls force_unicode
        on the default, which means you can't set arbitrary Python
        objects as the default. To fix this, we just return the value
        without calling force_unicode on it. Note that if you set a
        callable as a default, the field will still call it. It will
        *not* try to pickle and encode it.
        """
        if self.has_default():
            if callable(self.default):
                return self.default()
            return copy.deepcopy(self.default)
        # If the field doesn't have a default, then we punt to models.Field.
        return super(JSONField, self).get_default()


class DecimalJSONField(JSONField):
    """
    Custom field that dumps decimals as strings to keep precision and
    loads all floats as Decimals.
    """

    LOAD_KWARGS = {
        'parse_float': lambda x: Decimal(x)
    }


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^yajf\.fields\.JSONField"])
    add_introspection_rules([], ["^yajf\.fields\.DecimalJSONField"])
except ImportError:
    pass
