from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from japper import ec2utils
from .client import ConsulClient, parse_nagios_output


class MonitoringSource(MonitoringSourceBase):

    endpoints = models.TextField(help_text='List of consul HTTP endpoints, '
                                 'e.g. http://localhost:8500/')
    dynamic_hosts = models.BooleanField(
        default=False, help_text='Use this option when the list of hosts in '
        'this group is dynamic (e.g. when using autoscaling on EC2) and '
        'offline hosts should be removed instead of generating alerts')
    search_ec2_public_dns = models.BooleanField(
        default=False,
        help_text='Use EC2 API to retrieve the public DNS of the hosts from '
        'their default hostname')
    aws_region = models.CharField(max_length=255, blank=True, null=True)
    aws_access_key_id = models.CharField(max_length=255, blank=True, null=True)
    aws_secret_access_key = models.CharField(max_length=255, blank=True,
                                             null=True)

    def clean(self):
        if (self.search_ec2_public_dns and (
                not self.aws_region.strip() or
                not self.aws_access_key_id.strip() or
                not self.aws_secret_access_key.strip())):
            raise ValidationError('AWS credentials must be supplied to '
                                  'search EC2 public DNS names')

    @cached_property
    def checks_state(self):
        client = ConsulClient(self.endpoints.split())
        return client.get('/v1/health/state/any')

    def get_check_results(self):
        ret = []
        for check in self.checks_state:
            output, metrics = parse_nagios_output(check['Output'])
            status = Status.from_string(check['Status'])
            host = self.resolve_host(check['Node'])
            check_dict = {
                'name': check['CheckID'],
                'host': host,
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
                    host = self.resolve_host(check['Node'])
                    ret.append(host)
        return ret

    def has_dynamic_hosts(self):
        return self.dynamic_hosts

    def get_absolute_url(self):
        return reverse(
            'consul_update_monitoring_source',
            kwargs={'pk': self.pk}
        )

    def resolve_host(self, host):
        if self.search_ec2_public_dns:
            return ec2utils.search_public_dns(host,
                                              self.aws_region,
                                              self.aws_access_key_id,
                                              self.aws_secret_access_key)
        else:
            return host
