import copy

from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from celery import shared_task
from celery.utils.log import get_task_logger
from raven.contrib.django.raven_compat.models import client as raven_client

from japper.utils import report_to_sentry, single_instance
from .models import CheckResult, State
from .status import Status
from .plugins import iter_monitoring_backends, iter_alert_backends
from . import settings


logger = get_task_logger(__name__)


@shared_task
@report_to_sentry
@single_instance(60*3)
def fetch_check_results():
    '''
    Cron job fetching check results from monitoring backends.
    '''
    for backend in iter_monitoring_backends():
        for source in backend.get_instances(active=True):
            try:
                fetch_source_check_results(source)
            except Exception as exc:
                raven_client.captureException()
                status = Status.critical
                check_output = unicode(exc)
            else:
                status = Status.passing
                check_output = None

            # Also store a check result for the monitoring source
            source_health_name = '%s:health' % source
            check_obj = CheckResult(source=source, status=status,
                    name=source_health_name, host=source_health_name,
                    output=check_output)
            # Not sure if django sets auto_now_add fields in constructor,
            # better set it by hand
            check_obj.timestamp = timezone.now()
            state, _ = State.objects.get_or_create_from_check_result(check_obj)
            check_obj.state = state
            check_obj.save()

            # Analyze check results time series and update states
            source_type = ContentType.objects.get_for_model(source)
            for state in State.objects.filter(source_type=source_type,
                    source_id=source.pk):
                update_monitoring_states.delay(state.pk)


def fetch_source_check_results(source):
    # Get check results and removed hosts
    check_results = source.get_check_results()
    removed_hosts = set(source.get_removed_hosts())

    # Create CheckResult objects (only for new checks and hosts)
    for check_dict in check_results:
        check_obj = CheckResult.from_dict(source, check_dict)
        # Not sure if django sets auto_now_add fields in constructor,
        # better set it by hand
        check_obj.timestamp = timezone.now()
        if check_obj.host not in removed_hosts:
            state, _ = State.objects.get_or_create_from_check_result(check_obj)
            check_obj.state = state
            check_obj.save()

    # Delete removed hosts states
    source_type = ContentType.objects.get_for_model(source)
    State.objects.filter(source_type=source_type, source_id=source.pk,
            host__in=removed_hosts).delete()


@shared_task
@report_to_sentry
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
    results = list(CheckResult.objects.get_state_log(state,
            max_results=settings.MIN_CONSECUTIVE_STATUSES))
    if not len(results):
        # Not really sure why (probably a cache somewhere), but we sometimes
        # have states without check results
        return
    last_check_result = results[0]

    # Is there enough check results to do anything?
    do_send_alerts = False
    if len(results) >= settings.MIN_CONSECUTIVE_STATUSES:
        # If all previous check statuses are equal and different than the current
        # state status, update state
        statuses = [r.status for r in results]
        if statuses.count(statuses[0]) == len(statuses):
            if state.status != statuses[0]:
                state.status = statuses[0]
                state.last_status_change = last_check_result.timestamp
                if (not state.initial_bad_status_reported and
                        not state.status.is_problem()):
                    # Initial status was not OK, and it changed to an OK state
                    # before having enough check results to generate an alert.
                    # This was a "startup blip", so don't send an alert when
                    # the status goes back to normal.
                    pass
                else:
                    # Notify users of the status change
                    do_send_alerts = True
                    send_alerts_args = (prev_state, state)
                # Always set the initial_bad_status_reported flag here, to kill
                # initial status special cases once the status has changed
                state.initial_bad_status_reported = True
            elif (statuses[0].is_problem() and
                    not state.initial_bad_status_reported):
                # If state had initially a non-OK status, also send an alert
                # (only once)
                state.initial_bad_status_reported = True
                do_send_alerts = True
                send_alerts_args = (None, state)

    # Update state output and metrics if last check result and current state have
    # the same status. This avoids confusion during an alert (we show the
    # output of the check result when the alert started), and still show
    # up-to-date information when the state is stable.
    if last_check_result.status == state.status:
        state.output = last_check_result.output
        state.metrics = last_check_result.metrics

    # Always update last_checked timestamp
    state.last_checked = last_check_result.timestamp
    state.save()

    # Send alerts if needed
    if do_send_alerts:
        send_alerts.delay(*send_alerts_args)


@shared_task
@report_to_sentry
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
@report_to_sentry
def cleanup():
    '''
    Cron job to remove expired check results and states.
    '''
    now = timezone.now()
    states_date = now - settings.STATES_TTL
    checks_date = now - settings.CHECK_RESULTS_TTL
    for backend in iter_monitoring_backends():
        for source in backend.get_instances():
            source_type = ContentType.objects.get_for_model(source)
            if source.has_dynamic_hosts():
                State.objects.filter(source_type=source_type,
                        source_id=source.pk,
                        last_checked__lt=states_date).delete()
            CheckResult.objects.filter(source_type=source_type,
                    source_id=source.pk, timestamp__lt=checks_date).delete()
