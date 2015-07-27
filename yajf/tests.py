# -*- coding: utf-8 -*-
import mock
import django
from decimal import Decimal
from django.db import models
from django.test import TestCase

from .fields import JSONField, DecimalJSONField
from .encoder import JSONEncoder


class JsonModel(models.Model):
    value = JSONField()


class CustomJsonModel(models.Model):
    value = JSONField(load_kwargs={
        'parse_float': lambda x: Decimal(x)
    })


class JSONFieldNonDictTestCase(TestCase):
    model = JsonModel

    def test_saving_numbers(self):
        obj = self.model.objects.create(value=2.02)
        new_obj = self.model.objects.get(id=obj.id)

        self.assertEqual(new_obj.value, 2.02)

    def test_saving_strings_with_numbers(self):
        obj = self.model.objects.create(value='2.02')
        self.assertEqual(obj.value, '2.02')

        new_obj = self.model.objects.get(id=obj.id)
        self.assertEqual(new_obj.value, obj.value)

    def test_saving_dict(self):
        value = {'foo': 'bar'}
        obj = self.model.objects.create(value=value)
        self.assertIs(obj.value, value)

        new_obj = self.model.objects.get(id=obj.id)
        self.assertEqual(new_obj.value, obj.value)

    def test_attribution(self):
        obj = self.model()
        obj.value = '2.02'
        self.assertEqual(obj.value, '2.02')

        obj.save()
        new_obj = self.model.objects.get(id=obj.id)
        self.assertEqual(new_obj.value, obj.value)

    if django.VERSION[:2] >= (1, 8):
        @mock.patch.object(JSONField, 'from_db_value')
        @mock.patch.object(JSONField, 'to_python')
        def test_retrieve_calls_from_db_value(self, to_python, from_db_value):
            to_python.side_effect = lambda v: v
            obj = self.model.objects.create(value={'foo': 'bar'})
            from_db_value.return_value = obj.value

            new_obj = self.model.objects.get(id=obj.id)

            self.assertEqual(new_obj.value, obj.value)
            to_python.assert_any_call({'foo': 'bar'})
            self.assertNotIn(mock.call('{"foo":"bar"}'), to_python.call_args_list)
            args, kwargs = from_db_value.call_args
            self.assertEqual(args[0], '{"foo":"bar"}')

    def test_dumps_loads_helper_methods(self):
        obj = {
            'foo': {
                'bar': 42
            }
        }

        dumped = JSONField.dumps(obj)
        self.assertEqual(JSONField.loads(dumped), obj)

    def test_default_dumps_loads_kwargs(self):
        self.assertEqual(JSONField.LOAD_KWARGS, {})
        self.assertEqual(JSONField.DUMP_KWARGS, {
            'cls': JSONEncoder,
            'separators': (',', ':')
        })

    @mock.patch.object(JSONField, 'JSON_MODULE')
    def test_field_uses_loads_and_dumps(self, mock_json):
        JSONField.dumps({'foo': 'bar'})
        mock_json.dumps.assert_called_with({'foo': 'bar'}, **JSONField.DUMP_KWARGS)

        JSONField.loads('{"foo":"bar"}')
        mock_json.loads.assert_called_with('{"foo":"bar"}', **JSONField.LOAD_KWARGS)

    @mock.patch.object(JSONField, 'JSON_MODULE')
    def test_override_default_settings(self, mock_json):
        JSONField.dumps({'foo': 'bar'}, baz='quux')
        mock_json.dumps.assert_called_with({'foo': 'bar'}, baz='quux')

        JSONField.loads('{"foo":"bar"}', baz='quux')
        mock_json.loads.assert_called_with('{"foo":"bar"}', baz='quux')

    def test_decimal_precision_encoding(self):
        v = Decimal(0.1 + 0.2)

        dumped = JSONField.dumps(v)
        self.assertEqual(dumped, str(v))

        loaded = JSONField.loads(dumped)
        self.assertEqual(loaded, float(v))  # loses precision

    def test_decimal_json_field(self):
        v = Decimal(0.1 + 0.2)

        dumped = DecimalJSONField.dumps(v)
        loaded = DecimalJSONField.loads(dumped)

        self.assertIsInstance(loaded, Decimal)
        self.assertEqual(loaded, v)

    def test_custom_kwargs(self):
        obj = CustomJsonModel.objects.create(value=Decimal(0.1 + 0.2))
        new_obj = CustomJsonModel.objects.get(id=obj.id)
        self.assertEqual(new_obj.value, Decimal(0.1 + 0.2))

        obj = JsonModel.objects.create(value=Decimal(0.1 + 0.2))
        new_obj = JsonModel.objects.get(id=obj.id)
        self.assertEqual(new_obj.value, float(Decimal(0.1 + 0.2)))
