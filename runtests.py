#!/usr/bin/env python

from os.path import dirname, join
import sys


def configure_settings(options):
    from django.conf import settings

    # If DJANGO_SETTINGS_MODULE envvar exists the settings will be
    # configured by it. Otherwise it will use the parameters bellow.
    if not settings.configured:
        params = dict(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=('yajf',),
            MIDDLEWARE_CLASSES=(),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'yajf', 'tests'),
        )

        # Configure Django's settings
        settings.configure(**params)

    return settings


def get_runner(settings):
    '''
    Asks Django for the TestRunner defined in settings or the default one.
    '''
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests(options=None, labels=None):
    import django
    if not labels:
        labels = ['yajf']

    settings = configure_settings(options)
    if django.VERSION >= (1, 8):
        settings.TEST_RUNNER = 'django.test.runner.DiscoverRunner'

    runner = get_runner(settings)
    if django.VERSION >= (1, 7):
        django.setup()
    sys.exit(runner.run_tests(labels))

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename='/dev/null',
        filemode='a',
    )

    runtests()
