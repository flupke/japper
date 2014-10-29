'''
Interfaces for pluggable monitoring and alert backends.
'''

import six
from django.db.models.loading import get_model

from ..exceptions import ImproperlyConfigured
from .backend import Backend


class MonitoringBackend(Backend):
    '''
    Base class for monitoring backends plugins.
    '''

    name = None
    urls_module = None
    create_source_view = None
    monitoring_source_model = None

    def get_name(self):
        '''
        Return a descriptive name for the monitoring backend.
        '''
        if self.name is None:
            raise ImproperlyConfigured('subclasses of MonitoringBackend '
                    'must define the name property or reimplement get_name()')
        return self.name

    def get_urls_module(self):
        '''
        Return the dotted path to the urls module of the app.

        The default is the name of the package in which the backend class is
        defined appended with ``'.urls'``.  Define :attr:`urls_module` to
        override
        '''
        if self.urls_module is not None:
            return self.urls_module
        return '%s.urls' % self._guess_package()

    def get_create_source_view(self):
        '''
        Return the view name for creating a new monitoring source.
        '''
        if self.create_source_view is None:
            raise ImproperlyConfigured('subclasses of MonitoringBackend '
                    'must define the create_source_view property or '
                    'reimplement get_create_source_view()')
        return self.create_source_view

    def get_monitoring_sources(self, active=None):
        '''
        Return a queryset containing
        :class:`japper.monitoring.plugins.models.MonitoringSourceBase` objects
        for this monitoring backend.

        The default is to return all objects. If *active* is given, only active
        or inactive objects are returned.
        '''
        if self.monitoring_source_model is None:
            raise ImproperlyConfigured('subclasses of MonitoringBackend '
                    'must define the monitoring_source_model property '
                    'or reimplement get_monitoring_sources()')
        if isinstance(self.monitoring_source_model, six.string_types):
            model = get_model(self.monitoring_source_model)
        else:
            model = self.monitoring_source_model
        qs = model.objects.all()
        if active is not None:
            qs = qs.filter(active=active)
        return qs

