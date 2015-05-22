# -*- coding: utf-8 -*-
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
