import abc

import six
from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from ..models import CheckResult, State


class ABCModelMeta(abc.ABCMeta, ModelBase):

    pass


class BackendInstanceBase(six.with_metaclass(ABCModelMeta, models.Model)):

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class MonitoringSourceBase(BackendInstanceBase):
    '''
    Base model for monitoring sources.
    '''

    check_results = GenericRelation(CheckResult, related_query_name='sources',
            content_type_field='source_type', object_id_field='source_id')
    states = GenericRelation(State, related_query_name='sources',
            content_type_field='source_type', object_id_field='source_id')

    @abc.abstractmethod
    def get_check_results(self):
        '''
        Return a list of check results.

        This must return a list of dicts of the form::

            {
                'host': 'foo.com',
                'name': 'memory',
                'status': Status.passing,
                'output': 'OK - 75.0% used',
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

        The default implementation returns an empty list. Models returning
        something here should also probably implement
        :meth:`has_dynamic_hosts`.
        '''
        return []

    def get_content_type(self):
        '''
        Return the :class:`django.contrib.contenttypes.models.ContentType`
        object associated with this model.
        '''
        return ContentType.objects.get_for_model(self)

    def has_dynamic_hosts(self):
        '''
        Return a boolean indicating if this monitoring source has dynamic
        hosts.

        The default implementation returns False.
        '''
        return False

    class Meta:
        abstract = True


class AlertSinkBaseManager(models.Manager):

    def get_from_text_link(self, link):
        '''
        Retrieve an :class:`AlertSinkBase` object from *link*, generated by
        :meth:`AlertSinkBase.get_alert_sink_text_link`.
        '''
        content_type_pk, _, obj_pk = link.partition('/')
        content_type = ContentType.objects.get_for_id(content_type_pk)
        model = content_type.model_class()
        return model.objects.get(pk=obj_pk)


class AlertSinkBase(BackendInstanceBase):
    '''
    Base model for alert sinks.
    '''

    @abc.abstractmethod
    def send_alert(self, prev_state, new_state, user=None):
        '''
        Format and send an alert when a :class:`japper.monitoring.models.State`
        changes from *prev_state* to *new_state*.

        *user* may or may not be given depending on the scope of the sink
        (per-user or global), it is the responsibility of the implementation to
        send a message or not depending on its presence.

        *prev_state* may be None, in cases where a new state is created and is
        initially in a problem status.
        '''

    def get_alert_sink_text_link(self):
        '''
        Return a link that can be reversed (with the manager's
        :meth:`AlertSinkBaseManager.get_from_text_link` method) to retrieve
        this object.
        '''
        content_type = ContentType.objects.get_for_model(self)
        return '%s/%s' % (content_type.pk, self.pk)

    class Meta:
        abstract = True
