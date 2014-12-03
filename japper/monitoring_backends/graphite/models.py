import operator

from django.db import models
from django.core.urlresolvers import reverse

from japper.monitoring.plugins.models import MonitoringSourceBase


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(max_length=4096,
            help_text='The base URL of the graphite endpoint')

    def get_check_results(self):
        return []

    def get_absolute_url(self):
        return reverse('graphite_update_monitoring_source',
                kwargs={'pk': self.pk})

    def get_ui_entry_points(self):
        return [
            ('checks', reverse('graphite_checks', kwargs={'pk': self.pk})),
        ]


class Check(models.Model):

    OPERATORS = [
        (0, '<'),
        (1, '<='),
        (2, '=='),
        (3, '!='),
        (4, '>='),
        (5, '>'),
    ]
    OPERATOR_FUNCS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.ge,
        operator.gt,
    ]

    source = models.ForeignKey(MonitoringSource, related_name='checks',
            editable=False)

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    metric = models.CharField(max_length=4096)
    host = models.CharField(max_length=255, null=True, blank=True)
    warning_operator = models.SmallIntegerField(choices=OPERATORS)
    warning_value = models.FloatField()
    critical_operator = models.SmallIntegerField(choices=OPERATORS)
    critical_value = models.FloatField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graphite_update_check', kwargs={'pk': self.pk})
