'''
Interfaces for pluggable monitoring and alert backends.
'''

import abc

from enum import Enum
from django.db import models
from django.db.models.base import ModelBase
import six

from .exceptions import ImproperlyConfigured


class CheckStatus(Enum):

    passing = 1
    warning = 2
    critical = 3


class MonitoringBackend(six.with_metaclass(abc.ABCMeta, object)):
    '''
    Base class for monitoring backends plugins.
    '''

    monitoring_source_model = None
    name = None

    @abc.abstractmethod
    def get_create_source_view(self):
        '''
        Return the view name for creating a new monitoring source.
        '''

    def get_name(self):
        '''
        Return a descriptive name for the monitoring backend.
        '''
        if self.name is None:
            raise ImproperlyConfigured('subclasses of MonitoringBackend '
                    'must define the name property or reimplement get_name()')
        return self.name

    def get_monitoring_sources(self, active=None):
        '''
        Return a queryset containing :class:`MonitoringSource` objects foro
        this monitoring backend.

        The default is to return all objects. If active is given, only active
        or inactive objects are returned.
        '''
        if self.monitoring_sources_model is None:
            raise ImproperlyConfigured('subclasses of MonitoringBackend '
                    'must define the monitoring_source_model property '
                    'or reimplement get_monitoring_sources()')
        qs = self.monitoring_source_model.objects.all()
        if active is None:
            qs = qs.filter(active=active)
        return qs


class MonitoringSourceBase(ModelBase, abc.ABCMeta):

    pass


class MonitoringSource(six.with_metaclass(MonitoringSourceBase, models.Model)):
    '''
    Base model for monitoring sources.
    '''

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    @abc.abstractmethod
    def get_check_results(self):
        '''
        Return a list of check results.

        This must return a list of dicts of the form::

            {
                'host_name': 'foo.com',
                'check_name': 'memory',
                'status': CheckStatus.passing,
                'metrics': {
                    'free': '2G',
                    'used': '6G',
                    'swap': 0,
                },
            }

        Metrics must be a dict containing integers, floats or human-readable
        byte sizes values. It can also be None if the check does not have
        associated metrics.
        '''

    def get_removed_hosts(self):
        '''
        Return the list of hosts names that must be removed from monitoring.

        The default implementation returns an empty list.
        '''
        return []

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
