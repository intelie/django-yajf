#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, Command


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.conf import settings
        settings.configure(
                DATABASES={
                    'default': {
                        'NAME': ':memory:',
                        'ENGINE': 'django.db.backends.sqlite3'
                    }
                },
                INSTALLED_APPS=('yajf',),
                MIDDLEWARE_CLASSES=[]
        )
        from django.core.management import call_command
        import django
        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'yajf')


setup(
    name="django-yajf",
    version="0.4",
    url='https://github.com/intelie/django-yajf',
    author='Lucas Sampaio',
    author_email='lucas.sampaio@intelie.com.br',
    description='Yet Another JSONField for Django',
    include_package_data=True,
    install_requires=['Django>=1.6'],
    tests_require=['tox>=1.6.1', 'virtualenv>=1.11.1', 'mock==1.0.1'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Framework :: Django',
    ],
    license="Apache 2.0",
)
