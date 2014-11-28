from django.db import models
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from boto import ec2
from distributedlock import distributedlock

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from .client import Client, parse_nagios_output
from . import settings


class MonitoringSource(MonitoringSourceBase):

    endpoints = models.TextField(help_text='List of consul HTTP endpoints, e.g. '
            'http://localhost:8500/')
    dynamic_hosts = models.BooleanField(default=False, help_text='Use this '
            'option when the list of hosts in this group is dynamic (e.g. '
            'when using autoscaling on EC2) and offline hosts should be '
            'removed instead of generating alerts')
    search_ec2_public_dns = models.BooleanField(default=False,
            help_text='Use EC2 API to retrieve the public DNS of the hosts '
            'from their default hostname')
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
        client = Client(self.endpoints.split())
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
        return reverse('consul_update_monitoring_source',
                kwargs={'pk': self.pk})

    @cached_property
    def ec2_conn(self):
        return ec2.connect_to_region(self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key)

    @cached_property
    def ec2_instances(self):
        return self.ec2_conn.get_only_instances()

    def ec2_cache_key(self, host):
        return 'japper:consul:ec2_public_dns:%s' % host

    def resolve_host(self, host):
        if self.search_ec2_public_dns:

            # We don't want all celery workers to go crazy and update the cache
            # together, so we use a distributed lock here
            with distributedlock('consul_search_ec2_public_dns'):
                # Search in cache
                host_cache_key = self.ec2_cache_key(host)
                resolved_host = cache.get(host_cache_key)

                # If host was not found in cache, update cache
                if resolved_host is None:
                    known_instances = set()
                    for instance in self.ec2_instances:
                        if not instance.dns_name or not instance.private_dns_name:
                            continue
                        cache_key = self.ec2_cache_key(instance.private_dns_name)
                        cache.set(cache_key, instance.dns_name,
                                settings.EC2_DNS_NAMES_CACHE_TTL)
                        known_instances.add(instance.private_dns_name)
                    if host not in known_instances:
                        cache.set(host_cache_key, host)
                        return host
                else:
                    return resolved_host

                # Search again in cache, return original host if it's still not
                # found
                cache_key = self.ec2_cache_key(host)
                resolved_host = cache.get(cache_key)
                if resolved_host is None:
                    return host
                else:
                    return resolved_host

        return host
