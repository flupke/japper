from django.db import models
from django.utils.lru_cache import lru_cache

from japper.monitoring.plugins.models import MonitoringSourceBase, CheckStatus
from .client import Client, parse_nagios_output


class MonitoringSource(MonitoringSourceBase):

    endpoints = models.TextField(help_text='List of consul HTTP endpoints, e.g. '
            'http://localhost:8500/')
    dynamic_hosts = models.BooleanField(default=False, help_text='Use this '
            'option when the list of hosts in this group is dynamic (e.g. '
            'when using autoscaling on EC2) and offline hosts should be '
            'removed instead of generating alerts')

    @lru_cache()
    def get_checks_state(self):
        client = Client(self.endpoints.split())
        return client.request('GET', '/v1/health/state/any')

    def get_check_results(self):
        checks = self.get_checks_state()
        ret = []
        for check in checks:
            output, metrics = parse_nagios_output(check['Output'])
            status = CheckStatus.from_string(check['Status'])
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
        checks = self.get_checks_state()
        for check in checks:
            if check['CheckID'] == 'serfHealth':
                status = CheckStatus.from_string(check['Status'])
                if status is CheckStatus.critical:
                    ret.append(check['Node'])
        return ret

    @models.permalink
    def get_absolute_url(self):
        return ('consul_update_monitoring_source', [self.pk])
