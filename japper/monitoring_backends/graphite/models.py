import operator
import collections

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from raven.contrib.django.raven_compat.models import client as raven_client
from robgracli import GraphiteClient
from robgracli.client import average
from robgracli.exceptions import GraphiteException

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from japper.monitoring.models import State
from japper.ec2utils import search_public_dns


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(
        max_length=4096,
        help_text='The base URL of the graphite endpoint')
    aggregate_over = models.IntegerField(
        default=60,
        help_text='Aggregate metrics over this number of seconds')
    dynamic_hosts = models.BooleanField(
        default=False, help_text='Use this option when the list of hosts from '
        'this source is dynamic (e.g. when using autoscaling on EC2) and '
        'offline hosts should be removed instead of generating alerts')
    dead_hosts_query = models.TextField(
        blank=True,
        default='',
        help_text='A graphite search query that targets dead servers '
        'hostnames, used to remove dead dynamic hosts from Japper. For '
        'example if dead servers metrics are stored in '
        '"dead-servers.[hostname].cpu.idle", the query to target the hostname '
        'would be "dead-servers.*".')
    search_ec2_public_dns = models.BooleanField(
        default=False,
        help_text='Use EC2 API to retrieve the public DNS of the hosts from '
        'their default hostname')
    aws_region = models.CharField(max_length=255, blank=True, null=True)
    aws_access_key_id = models.CharField(max_length=255, blank=True, null=True)
    aws_secret_access_key = models.CharField(max_length=255, blank=True,
                                             null=True)

    def get_check_results(self):
        client = self.create_client()
        ret = []
        for check in self.checks.all():
            ret.extend(check.run(self, client, self.aggregate_over))
        if self.search_ec2_public_dns:
            for check_dict in ret:
                public_dns = search_public_dns(check_dict['host'],
                                               self.aws_region,
                                               self.aws_access_key_id,
                                               self.aws_secret_access_key)
                if public_dns is not None:
                    check_dict['host'] = public_dns
        return ret

    def create_client(self):
        return GraphiteClient(self.endpoint)

    def get_absolute_url(self):
        return reverse('graphite_update_monitoring_source',
                       kwargs={'pk': self.pk})

    def get_ui_entry_points(self):
        return [
            ('checks', reverse('graphite_checks', kwargs={'pk': self.pk})),
        ]

    def has_dynamic_hosts(self):
        return self.dynamic_hosts

    def get_removed_hosts(self):
        if not self.dynamic_hosts:
            return []
        client = self.create_client()
        result = client.find_metrics(self.dead_hosts_query)
        hostnames = [e['text'] for e in result]
        if self.search_ec2_public_dns:
            ret = []
            for host in hostnames:
                public_dns = search_public_dns(host,
                                               self.aws_region,
                                               self.aws_access_key_id,
                                               self.aws_secret_access_key)
                if public_dns is not None:
                    ret.append(public_dns)
                else:
                    ret.append(host)
        else:
            ret = hostnames
        return ret

    def get_associated_states_hosts(self):
        content_type = ContentType.objects.get_for_model(self)
        states = State.objects.filter(
            source_type=content_type,
            source_id=self.pk,
        )
        return {s.host for s in states}


class Check(models.Model):

    LT = 0
    LE = 1
    EQ = 2
    NE = 3
    GE = 4
    GT = 5
    OPERATORS = [
        (LT, '<'),
        (LE, '<='),
        (EQ, '=='),
        (NE, '!='),
        (GE, '>='),
        (GT, '>'),
    ]
    OPERATOR_FUNCS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.ge,
        operator.gt,
    ]
    AVERAGE = 0
    MAX = 1
    MIN = 2
    AGGREGATORS = [
        (AVERAGE, 'average'),
        (MAX, 'max'),
        (MIN, 'min'),
    ]
    AGGREGATOR_FUNCS = [average, max, min]
    PROBLEM_FMT = '{metric} {operator} {threshold_value} ({value})'
    PASSING_FMT = '{metric} {operator} {value}'

    source = models.ForeignKey(MonitoringSource, related_name='checks',
                               editable=False)

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    query = models.TextField(
        help_text='The graphite query to evaluate, you may use functions '
        'here. It may output multiple metrics.')
    matrix_metrics = models.BooleanField(
        default=False,
        help_text='If checked, expect a matrix result from the graphite '
        'query. This means that the metrics returned are indexed by hostname '
        'and some other axis. For example if you have disk metrics indexed '
        'by hostname and mount point, e.g. '
        '"servers.[hostname].disk.[mount_point].free_percent", metrics '
        'should be aliased as "[hostname].[mount_point]" (using the '
        '"aliasSub()" graphite function). It will produce [num_hostnames] * '
        '[num_mount_points] separate checks.')
    metric_aggregator = models.SmallIntegerField(
        choices=AGGREGATORS,
        default=AVERAGE,
        help_text='The last 1 minute of values are aggregated using this '
        'function. The result is then compared to the threshold values '
        'below.')
    host = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Host name to associate with this check. If left blank, '
        'use the target name(s) in the graphite query result')
    warning_operator = models.SmallIntegerField(choices=OPERATORS, default=GE)
    warning_value = models.FloatField()
    critical_operator = models.SmallIntegerField(choices=OPERATORS, default=GE)
    critical_value = models.FloatField()

    def run(self, source, client, aggregate_over=60):
        # Query graphite
        agg_func = self.AGGREGATOR_FUNCS[self.metric_aggregator]
        try:
            result = client.aggregate(self.query,
                                      aggregate_over,
                                      agg_func)
        except GraphiteException as exc:
            raven_client.captureException()
            hosts = source.get_associated_states_hosts()
            ret = []
            for host in hosts:
                check_dict = self._build_check_dict(
                    Status.unknown,
                    'unexpected error: %s' % exc,
                    host
                )
                ret.append(check_dict)
            return ret
        # Aggregate metrics by host
        metrics = collections.defaultdict(dict)
        for target, value in result.items():
            host, name = self._get_host_and_name_from_target(target)
            metrics[host][name] = value
        # Create checks
        ret = []
        for host, metrics in metrics.items():
            check_dict = self._check_metrics(host, metrics)
            ret.append(check_dict)
        return ret

    def _get_host_and_name_from_target(self, target):
        if self.host.strip() != '':
            host = self.host
            name = self.name
        else:
            if self.matrix_metrics:
                host, _, name = target.partition('.')
            else:
                host = target
                name = self.name
        return host, name

    def _check_metrics(self, host, metrics):
        warning_func = self.OPERATOR_FUNCS[self.warning_operator]
        critical_func = self.OPERATOR_FUNCS[self.critical_operator]
        status = None
        critical = False
        warning = False
        outputs = []
        for metric_name, metric_value in metrics.items():
            if metric_value is None:
                # A single unknown value is sufficient to make the whole check
                # fail with an unknown state
                return self._build_check_dict(
                    Status.unknown,
                    'got no valid data points for "%s"' % metric_name,
                    host
                )
            if critical_func(metric_value, self.critical_value):
                critical = True
                output = self.PROBLEM_FMT.format(
                    metric=metric_name,
                    operator=self.get_critical_operator_display(),
                    threshold_value=self.critical_value,
                    value=metric_value
                )
            elif warning_func(metric_value, self.warning_value):
                warning = True
                output = self.PROBLEM_FMT.format(
                    metric=metric_name,
                    operator=self.get_warning_operator_display(),
                    threshold_value=self.warning_value,
                    value=metric_value
                )
            else:
                status = Status.passing
                output = self.PASSING_FMT.format(
                    metric=metric_name,
                    operator='=',
                    value=metric_value
                )
            outputs.append(output)
        if critical:
            status = Status.critical
        elif warning:
            status = Status.warning
        else:
            status = Status.passing
        output = '%s - %s' % (status.name, ', '.join(outputs))
        return self._build_check_dict(
            status,
            output,
            host,
            metrics=metrics
        )

    def _build_check_dict(self, status, output, host, metrics={}):
        return {
            'name': self.name,
            'host': host,
            'status': status,
            'output': output,
            'metrics': metrics,
        }

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graphite_update_check', kwargs={'pk': self.pk})
