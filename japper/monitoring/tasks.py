from django.contrib.contenttypes.models import ContentType
from celery import shared_task

from .models import CheckResult, State, StateStatus
from .plugins import iter_monitoring_backends
from . import settings


@shared_task
def fetch_check_results():
    '''
    Cron job fetching check results from monitoring backends.
    '''
    for backend in iter_monitoring_backends():
        for source in backend.get_monitoring_sources(active=True):
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
                    status = StateStatus.from_check_status(check_obj.status)
                    State.objects.get_or_create(
                        source_type=source_content_type,
                        source_id=source.pk,
                        name=check_obj.name,
                        host=check_obj.host,
                        defaults={
                            'status': status,
                            'output': check_obj.output,
                            'metrics': check_obj.metrics,
                        }
                    )

            # Delete removed hosts
            State.objects.filter(source_type=source_content_type,
                    source_id=source.pk, host__in=removed_hosts).delete()

            # Analyze check results time series and update remaining states
            for state in State.objects.filter(source_type=source_content_type,
                    source_id=source.pk):
                update_monitoring_state.delay(state.pk)


@shared_task
def update_monitoring_state(state_pk):
    '''
    Subtask called from :func:`fetch_check_results`, looks back at check
    results history for a state and updates it accordingly.
    '''
    try:
        state = State.objects.get(pk=state_pk)
    except State.DoesNotExist:
        return

    # Retrieve last check results
    results = CheckResult.objects\
        .filter(
            source_type=state.source_type,
            source_id=state.source_id,
            host=state.host,
            name=state.name)\
        .order_by('-timestamp')[:settings.MIN_CONSECUTIVE_STATUSES]

    # Is there enough check results to take a decision?
    if results.count() < settings.MIN_CONSECUTIVE_STATUSES:
        return

    # If all previous statuses are equal and different than the current state
    # status, update state
    statuses = [r.status for r in results]
    if statuses.count(statuses[0]) == len(statuses):
        state_status = StateStatus.from_check_status(statuses[0])
        if state.status != state_status:
            state.status = state_status
            state.save(update_fields=['status'])
