import abc

import six
from enum import Enum
from django.db import models
from django.db.models.base import ModelBase


class CheckStatus(Enum):

    passing = 1
    warning = 2
    critical = 3


class MonitoringSourceMeta(abc.ABCMeta, ModelBase):

    pass


class MonitoringSourceBase(six.with_metaclass(MonitoringSourceMeta,
        models.Model)):
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
