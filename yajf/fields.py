# -*- coding: utf-8 -*-
import six
import copy
import json
import django
import inspect
from django.db import models
from .encoder import JSONEncoder


class JSONField(six.with_metaclass(models.SubfieldBase, models.Field)):
    MUST_CHECK_STACK = django.VERSION < (1, 8)

    def __init__(self, *args, **kwargs):
        self.json = kwargs.pop('json_module', json)
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        self.dump_kwargs = kwargs.pop('dump_kwargs', {
            'cls': JSONEncoder,
            'separators': (',', ':')
        })

        super(JSONField, self).__init__(*args, **kwargs)

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

        return self.json.loads(value, **self.load_kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""

        if value is None and self.null:
            return None

        if isinstance(value, bytes):
            value = value.decode('utf-8')

        value = self.json.dumps(value, **self.dump_kwargs)
        return value

    def value_to_string(self, obj):
        value = self._get_value_from_obj(obj)
        return self.get_db_prep_value(value, None)

    def value_from_object(self, obj):
        value = super(JSONField, self).value_from_object(obj)
        if self.null and value is None:
            return None
        return self.dumps_for_display(obj)

    def dumps_for_display(self, value):
        return json.dumps(value, **self.dump_kwargs)

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
