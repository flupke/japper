#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


setup_requires = []

if 'test' in sys.argv:
    setup_requires.append('pytest')

dev_requires = []

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-django',
    'pytest-timeout',
    'unittest2',
]

install_requires = [
    'Django==1.7.1',
    'django-crispy-forms==1.4.0',
    'django-paging==0.2.5',
    'enum34==1.0.3',
    'django-enumfields==0.5.1',
    'requests==2.4.3',
    'django-vanilla-views==1.0.3',
    'django-environ==0.3.0',
    'jsonfield==1.0.0',
    'celery==3.1.16',
    'django-simple-menu==1.0.9',
]

postgres_requires = [
    'psycopg2==2.5.4',
]

mysql_requires = [
    'MySQL-python==1.2.5',
]


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['japper']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='japper',
    version='0.0.1-DEV',
    author='Luper Rouch',
    author_email='luper.rouch@gmail.com',
    url='https://github.com/Stupeflix/japper',
    description='A multi backend alerting tool',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'dev': dev_requires,
        'postgres': install_requires + postgres_requires,
        'mysql': install_requires + mysql_requires,
    },
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    license='MPL 2.0',
    include_package_data=True,
    entry_points={
        'japper.monitoring_backends': [
            'consul = japper.monitoring_backends.consul.plugin:create_backend',
        ],
        'japper.alert_backends': [
            'django_email = japper.alert_backends.django_email.plugin:create_backend',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
