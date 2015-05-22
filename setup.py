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
                INSTALLED_APPS=('better_jsonfield',),
                MIDDLEWARE_CLASSES=[]
        )
        from django.core.management import call_command
        import django
        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'better_jsonfield')


setup(
    name="better-jsonfield",
    version="0.4",
    url='https://github.com/intelie/jsonfield',
    author='Vitor M. A. da Cruz',
    author_email='vitor.mazzi@intelie.com.br',
    description='',
    long_description='',
    packages=['better_jsonfield'],
    include_package_data=True,
    install_requires=['Django>=1.6'],
    tests_require=['tox>=1.6.1', 'virtualenv>=1.11.1'],
    cmdclass={'test': TestCommand},
    classifiers=[
        'Framework :: Django',
    ],
    license="Apache 2.0",
)
