import operator

from django.db import models
from django.core.urlresolvers import reverse
from raven.contrib.django.raven_compat.models import client as raven_client

from japper.monitoring.plugins.models import MonitoringSourceBase
from japper.monitoring.status import Status
from .client import GraphiteClient, average
from .exceptions import InvalidDataFormat, EmptyData


class MonitoringSource(MonitoringSourceBase):

    endpoint = models.CharField(
        max_length=4096,
        help_text='The base URL of the graphite endpoint')
    dynamic_hosts = models.BooleanField(
        default=False, help_text='Use this option when the list of hosts from '
        'this source is dynamic (e.g. when using autoscaling on EC2) and '
        'offline hosts should be removed instead of generating alerts')
    dead_hosts_query = models.TextField(
        max_length=4096,
        help_text='A graphite query that targets dead servers, used to remove '
        'dead dynamic hosts from Japper.')
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
            ret.append(check.run(client))
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
        client.get_metric(self.dead_hosts_query, allow_multiple=True)


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
    PROBLEM_FMT = '{status} - {metric} {operator} {threshold_value} ({value})'
    PASSING_FMT = '{status} - {metric} {operator} {value}'

    source = models.ForeignKey(MonitoringSource, related_name='checks',
                               editable=False)

    name = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    query = models.TextField(
        max_length=4096,
        help_text='The graphite query to evaluate, If it returns '
        'multiple metrics, the target name is used to fill the host.')
    metric_aggregator = models.SmallIntegerField(
        choices=AGGREGATORS,
        default=AVERAGE,
        help_text='The last 1 minute of values are aggregated using this '
        'function. The result is then compared to the threshold values '
        'below.')
    host = models.CharField(max_length=255, null=True, blank=True)
    warning_operator = models.SmallIntegerField(choices=OPERATORS, default=GE)
    warning_value = models.FloatField()
    critical_operator = models.SmallIntegerField(choices=OPERATORS, default=GE)
    critical_value = models.FloatField()

    def run(self, client):
        try:
            agg_func = self.AGGREGATOR_FUNCS[self.metric_aggregator]
            try:
                value = client.get_metric(self.target, aggregator=agg_func)
            except (InvalidDataFormat, EmptyData) as exc:
                return self.build_check_dict(Status.unknown, str(exc))
            warning_func = self.OPERATOR_FUNCS[self.warning_operator]
            critical_func = self.OPERATOR_FUNCS[self.critical_operator]
            if critical_func(value, self.critical_value):
                status = Status.critical
                operator = self.get_critical_operator_display()
                threshold_value = self.critical_value
                output_fmt = self.PROBLEM_FMT
            elif warning_func(value, self.warning_value):
                status = Status.warning
                operator = self.get_warning_operator_display()
                threshold_value = self.warning_value
                output_fmt = self.PROBLEM_FMT
            else:
                status = Status.passing
                operator = '='
                threshold_value = None
                output_fmt = self.PASSING_FMT
            output = output_fmt.format(
                status=status.name,
                metric=self.name,
                operator=operator,
                threshold_value=threshold_value,
                value=value
            )
            return self.build_check_dict(status, output,
                                         metrics={self.name: value})
        except Exception as exc:
            raven_client.captureException()
            return self.build_check_dict(Status.unknown,
                                         'unexpected error: %s' % exc)

    def build_check_dict(self, status, output=None, metrics={}):
        return {
            'name': self.name,
            'host': self.host,
            'status': status,
            'output': output,
            'metrics': metrics,
        }

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('graphite_update_check', kwargs={'pk': self.pk})

