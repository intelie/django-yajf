#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    user_options = TestCommand.user_options + [
        ('environment=', 'e', "Run 'test_suite' in specified environment")
    ]
    environment = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        if self.environment:
            self.test_args.append('-e{0}'.format(self.environment))
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


def get_readme():
    """Return the README file contents. Supports text,rst, and markdown"""
    for name in ('README', 'README.rst', 'README.md'):
        if os.path.exists(name):
            return read_file(name)
    return ''


setup(
    name="django-yajf",
    version="0.5.0",
    url='https://github.com/intelie/django-yajf',
    author='Lucas Sampaio',
    author_email='lucas.sampaio@intelie.com.br',
    description='Yet Another JSONField for Django',
    long_description=get_readme(),
    include_package_data=True,
    packages=find_packages(exclude=["example", "*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=['Django>=1.6'],
    tests_require=['virtualenv>=1.11.2', 'tox>=1.6.1', 'mock==1.0.1'],
    cmdclass={'test': Tox},
    test_suite='yajf.tests',
    classifiers=[
        'Framework :: Django',
    ],
    license="Apache 2.0",
)
