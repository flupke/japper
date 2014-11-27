from django.db import models
from django.core.urlresolvers import reverse

from japper.monitoring.plugins.models import MonitoringSourceBase


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(max_length=255,
            help_text='The URL of the graphite, endpoint')

    def get_check_results(self):
        return []

    def get_absolute_url(self):
        return reverse('graphite_update_monitoring_source',
                kwargs={'pk': self.pk})

