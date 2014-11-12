from django.db import models
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from .client import Client, parse_nagios_output


class MonitoringSource(MonitoringSourceBase):

    endpoints = models.TextField(help_text='List of consul HTTP endpoints, e.g. '
            'http://localhost:8500/')
    dynamic_hosts = models.BooleanField(default=False, help_text='Use this '
            'option when the list of hosts in this group is dynamic (e.g. '
            'when using autoscaling on EC2) and offline hosts should be '
            'removed instead of generating alerts')

    @cached_property
    def checks_state(self):
        client = Client(self.endpoints.split())
        return client.request('GET', '/v1/health/state/any')

    def get_check_results(self):
        ret = []
        for check in self.checks_state:
            output, metrics = parse_nagios_output(check['Output'])
            status = Status.from_string(check['Status'])
            check_dict = {
                'name': check['CheckID'],
                'host': check['Node'],
                'status': status,
                'output': output,
                'metrics': metrics,
            }
            ret.append(check_dict)
        return ret

    def get_removed_hosts(self):
        if not self.dynamic_hosts:
            return []
        ret = []
        for check in self.checks_state:
            if check['CheckID'] == 'serfHealth':
                status = Status.from_string(check['Status'])
                if status is Status.critical:
                    ret.append(check['Node'])
        return ret

    def has_dynamic_hosts(self):
        return self.dynamic_hosts

    def get_absolute_url(self):
        return reverse('consul_update_monitoring_source',
                kwargs={'pk': self.pk})
