from django.db import models
from django.core.urlresolvers import reverse
from enumfields import EnumIntegerField

from japper.monitoring.plugins.models import MonitoringSourceBase
from .operator import Operator


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(max_length=4096,
            help_text='The base URL of the graphite endpoint')

    def get_check_results(self):
        return []

    def get_absolute_url(self):
        return reverse('graphite_update_monitoring_source',
                kwargs={'pk': self.pk})


class Check(models.Model):

    source = models.ForeignKey(MonitoringSource)

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    metric = models.CharField(max_length=4096)
    host = models.CharField(max_length=255, null=True, blank=True)
    warning_operator = EnumIntegerField(Operator)
    warning_value = models.FloatField()
    critical_operator = EnumIntegerField(Operator)
    critical_value = models.FloatField()
