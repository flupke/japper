from collections import Counter

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField
from enumfields import EnumIntegerField

from .status import Status


class CheckResult(models.Model):
    '''
    The result of a check.

    These are raw time series, evaluated to produce State objects.
    '''

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    source_type = models.ForeignKey(ContentType)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')

    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255, null=True)
    status = EnumIntegerField(Status)
    output = models.CharField(max_length=255, null=True)
    metrics = JSONField(null=True)

    @classmethod
    def from_dict(cls, source, data):
        return cls(source=source, **data)

    class Meta:
        index_together = ['source_type', 'source_id']


class State(models.Model):
    '''
    The current state for a service or a node.
    '''

    source_type = models.ForeignKey(ContentType)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')

    name = models.CharField(max_length=255, db_index=True)
    host = models.CharField(max_length=255, db_index=True, null=True)
    status = EnumIntegerField(Status, db_index=True)
    output = models.CharField(max_length=255, null=True)
    metrics = JSONField(null=True)

    last_checked = models.DateTimeField()
    last_status_change = models.DateTimeField(null=True)

    class Meta:
        unique_together = ['source_type', 'source_id', 'host', 'name']

    @classmethod
    def group_by_host(cls, states):
        '''
        Build a list of (host, states, status_counter) tuples out of the
        *states* iterable.
        '''

        def host_group_data(host, states):
            status_counter = Counter()
            for state in states:
                status_counter[state.status.name] += 1
            return (host, states, status_counter)

        prev_host = no_host = object()
        host_states = []
        states_by_host = []
        for state in states:
            if prev_host != no_host and state.host != prev_host:
                states_by_host.append(host_group_data(prev_host, host_states))
                host_states = []
            host_states.append(state)
            prev_host = state.host

        if host_states:
            states_by_host.append(host_group_data(prev_host, host_states))

        return states_by_host
