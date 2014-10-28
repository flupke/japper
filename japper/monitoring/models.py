from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from enum import Enum
from jsonfield import JSONField
from enumfields import EnumIntegerField

from .plugins.models import CheckStatus


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
    status = EnumIntegerField(CheckStatus)
    output = models.CharField(max_length=255, null=True)
    metrics = JSONField(null=True)

    @classmethod
    def from_dict(cls, source, data):
        return cls(source=source, **data)

    class Meta:
        index_together = ['source_type', 'source_id']


class StateStatus(Enum):

    passing = 1
    warning = 2
    critical = 3
    unknown = 4
    flapping = 5

    @classmethod
    def from_check_status(cls, status):
        if status == CheckStatus.passing:
            return cls.passing
        elif status == CheckStatus.warning:
            return cls.warning
        elif status == CheckStatus.critical:
            return cls.critical
        elif status == CheckStatus.warning:
            return cls.warning
        raise ValueError('invalid status: %s' % status)


class State(models.Model):
    '''
    The current state for a service or a node.
    '''

    source_type = models.ForeignKey(ContentType)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')

    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255, db_index=True, null=True)
    status = EnumIntegerField(StateStatus, db_index=True)
    metrics = JSONField(null=True)

    last_checked = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        unique_together = ['source_type', 'source_id', 'host', 'name']
