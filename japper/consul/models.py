from django.db import models
from japper.monitoring.plugins.models import MonitoringSourceBase


class MonitoringSource(MonitoringSourceBase):

    endpoints = models.TextField(help_text='List of consul HTTP endpoints, e.g. '
            'http://localhost:8500/')
    dynamic_hosts = models.BooleanField(default=False, help_text='Use this '
            'option when the list of hosts in this group is dynamic (e.g. '
            'when using autoscaling on EC2) and offline hosts should be '
            'removed instead of generating alerts')

    def get_check_results(self):
        return []

    @models.permalink
    def get_absolute_url(self):
        return ('consul_update_monitoring_source', [self.pk])
