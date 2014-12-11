import six
from collections import Counter, defaultdict
import humanfriendly

from django.db import models
from django.utils.functional import cached_property
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField
from enumfields import EnumIntegerField

from .status import Status


class CheckResultManager(models.Manager):

    def get_state_log(self, state, reverse=True, max_results=100):
        '''
        Get a query set containing the check results associated with
        :class:`State` object *state*.

        Results are given in reverse order, unless *reverse* is False.
        '''
        if reverse:
            order_by = '-timestamp'
        else:
            order_by = 'timestamp'
        return self.filter(state=state).order_by(order_by)[:max_results]


class CheckResult(models.Model):
    '''
    The result of a check.

    These are raw time series, evaluated to produce State objects.
    '''

    objects = CheckResultManager()

    state = models.ForeignKey('State', related_name='check_results')
    source_type = models.ForeignKey(ContentType)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')

    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255, null=True)
    status = EnumIntegerField(Status)
    output = models.CharField(max_length=4095, null=True)
    metrics = JSONField(null=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    @classmethod
    def from_dict(cls, source, data):
        return cls(source=source, **data)

    class Meta:
        index_together = ['source_type', 'source_id']


class StateManager(models.Manager):

    def get_or_create_from_check_result(self, check_result):
        source = check_result.source
        source_content_type = ContentType.objects.get_for_model(source)
        return self.get_or_create(
            source_type=source_content_type,
            source_id=source.pk,
            name=check_result.name,
            host=check_result.host,
            defaults={
                'status': check_result.status,
                'output': check_result.output,
                'metrics': check_result.metrics,
                'last_checked': check_result.timestamp,
            }
        )


class State(models.Model):
    '''
    The current state for a service or a node.
    '''

    objects = StateManager()

    source_type = models.ForeignKey(ContentType)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')

    name = models.CharField(max_length=255, db_index=True)
    host = models.CharField(max_length=255, db_index=True, null=True)
    status = EnumIntegerField(Status, db_index=True)
    output = models.CharField(max_length=4095, null=True)
    metrics = JSONField(null=True)

    first_seen = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField()
    last_status_change = models.DateTimeField(null=True)
    initial_bad_status_reported = models.BooleanField(default=False)

    class Meta:
        unique_together = ['source_type', 'source_id', 'host', 'name']

    @classmethod
    def group_by_host(cls, states):
        '''
        Build a list of (host, states, status_counter, oldest_problem_date,
        might_be_starting, has_problems) tuples out of the *states* iterable.
        '''

        def host_group_data(host, states):
            status_counter = Counter()
            oldest_problem_date = None
            might_be_starting = True
            has_problems = False
            for state in states:
                status_counter[state.status.name] += 1
                if state.status.is_problem():
                    if oldest_problem_date is None:
                        oldest_problem_date = state.last_status_change
                    else:
                        if state.last_status_change is not None:
                            oldest_problem_date = min(oldest_problem_date,
                                    state.last_status_change)
                    has_problems = True
                if state.initial_bad_status_reported:
                    might_be_starting = False
            return (host, states, status_counter, oldest_problem_date,
                    might_be_starting, has_problems)

        prev_host = no_host = object()
        host_states = []
        states_by_host = []
        for state in states:
            if prev_host != no_host and state.host != prev_host:
                states_by_host.append(host_group_data(prev_host, host_states))
                host_states = []
            host_states.append(state)
            prev_host = state.host

        if host_states:
            states_by_host.append(host_group_data(prev_host, host_states))

        return states_by_host

    @cached_property
    def metrics_series(self):
        '''
        Aggregate check results metrics series attached to this state.
        '''
        results = CheckResult.objects.get_state_log(self, max_results=1000)
        metrics = defaultdict(list)
        for result in reversed(results):
            for name, value in result.metrics.items():
                if isinstance(value, six.string_types):
                    try:
                        value = humanfriendly.parse_size(value)
                    except humanfriendly.InvalidSize:
                        continue
                metrics[name].append((result.timestamp, value))
        # Disable default_factory in defaultdict so it can be used in django
        # templates
        metrics.default_factory = None
        return metrics

    def __unicode__(self):
        return self.name

    def full_path(self):
        if self.host:
            suffix = u'%s/%s' % (self.host, self.name)
        else:
            suffix = self.name
        return u'/%s/%s' % (self.source, suffix)

    @models.permalink
    def get_absolute_url(self):
        return 'monitoring_state_detail', [self.pk]


