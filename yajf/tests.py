# -*- coding: utf-8 -*-
import mock
import django
from django.db import models
from django.test import TestCase
from .fields import JSONField


class JsonModel(models.Model):
    value = JSONField()


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
