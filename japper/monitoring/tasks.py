import copy

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from celery import shared_task
from celery.utils.log import get_task_logger

from .models import CheckResult, State
from .plugins import iter_monitoring_backends, iter_alert_backends
from . import settings


logger = get_task_logger(__name__)


@shared_task
def fetch_check_results():
    '''
    Cron job fetching check results from monitoring backends.
    '''
    for backend in iter_monitoring_backends():
        for source in backend.get_instances(active=True):
            # Get ContentType of the source model for filtering querysets
            source_content_type = ContentType.objects.get_for_model(source)

            # Get check results and removed hosts
            check_results = source.get_check_results()
            removed_hosts = set(source.get_removed_hosts())

            # Create CheckResult objects (only for new checks and hosts)
            for result in check_results:
                check_obj = CheckResult.from_dict(source, result)
                check_obj.save()
                if check_obj.host not in removed_hosts:
                    State.objects.get_or_create(
                        source_type=source_content_type,
                        source_id=source.pk,
                        name=check_obj.name,
                        host=check_obj.host,
                        defaults={
                            'status': check_obj.status,
                            'output': check_obj.output,
                            'metrics': check_obj.metrics,
                            'last_checked': check_obj.timestamp,
                        }
                    )

            # Delete removed hosts
            State.objects.filter(source_type=source_content_type,
                    source_id=source.pk, host__in=removed_hosts).delete()

            # Analyze check results time series and update remaining states
            for state in State.objects.filter(source_type=source_content_type,
                    source_id=source.pk):
                update_monitoring_states.delay(state.pk)


@shared_task
def update_monitoring_states(state_pk):
    '''
    Subtask called from :func:`fetch_check_results`, looks back at check
    results history for a state and updates it accordingly.
    '''
    try:
        state = State.objects.get(pk=state_pk)
    except State.DoesNotExist:
        return
    prev_state = copy.deepcopy(state)

    # Retrieve last check results
    results = CheckResult.objects.get_state_log(state,
            max_results=settings.MIN_CONSECUTIVE_STATUSES)

    # Is there enough check results to take a decision?
    if results.count() < settings.MIN_CONSECUTIVE_STATUSES:
        return
    last_check_result = results[0]

    # If all previous check statuses are equal and different than the current
    # state status, update state
    statuses = [r.status for r in results]
    if statuses.count(statuses[0]) == len(statuses):
        if state.status != statuses[0]:
            state.status = statuses[0]
            state.ouptut = last_check_result.output
            state.metrics = last_check_result.metrics
            state.last_status_change = last_check_result.timestamp
            # Notify users of the status change
            send_alerts.delay(prev_state, state)

    # Always update last_checked timestamp
    state.last_checked = last_check_result.timestamp
    state.save()


@shared_task
def send_alerts(prev_state, new_state):
    '''
    Send alert to all sinks and all users subscribed to them.
    '''
    for backend in iter_alert_backends():
        for sink in backend.get_instances(active=True):
            sink.send_alert(prev_state, new_state)
            sink_link = sink.get_alert_sink_text_link()
            for user in User.objects.filter(is_active=True,
                    profile__subscriptions__contains=sink_link):
                sink.send_alert(prev_state, new_state, user=user)
                logger.warning('sent alert to %s', user)


@shared_task
def cleanup():
    '''
    Cron job to remove expired check results and states.
    '''
    now = timezone.now()
    CheckResult.objects.filter(
            timestamp__lt=now - settings.CHECK_RESULTS_TTL).delete()
    State.objects.filter(
            last_checked__lt=now - settings.STATES_TTL).delete()
