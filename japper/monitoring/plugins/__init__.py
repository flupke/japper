import itertools

import pkg_resources
from django.conf.urls import patterns, include, url


def iter_monitoring_backends():
    '''
    Iterate over registered monitoring backends objects.
    '''
    for entry_point in pkg_resources.iter_entry_points(
            'japper.monitoring_backends'):
        func = entry_point.load()
        yield func()


def get_installed_apps(base_apps):
    '''
    Build the INSTALLED_APPS setting, extending *base_apps* with registered
    backend apps.
    '''
    monitoring_backends_apps = (b.get_app_name()
            for b in iter_monitoring_backends())
    return tuple(itertools.chain(base_apps, monitoring_backends_apps))


def get_url_patterns(prefix, *base_urls):
    '''
    Build the main app URL patterns.

    This is a drop-in replacement for :func:`django.conf.urls.patterns`, just
    replace it whith this function in your main ``urls.py`` file.
    '''
    monitoring_backends_urls = (
            url(r'^%s/' % b.get_name(), include(b.get_urls_module()))
            for b in iter_monitoring_backends())
    return patterns(prefix,
            *itertools.chain(base_urls, monitoring_backends_urls))
