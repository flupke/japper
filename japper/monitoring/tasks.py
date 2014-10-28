from django.contrib.contenttypes.models import ContentType
from celery import shared_task

from .models import CheckResult, State, StateStatus
from .plugins import iter_monitoring_backends


@shared_task
def update_monitoring_states():
    '''
    Cron job updating monitoring states from the output of monitoring backends.
    '''
    for backend in iter_monitoring_backends():
        for source in backend.get_monitoring_sources(active=True):
            # Get ContentType of the source model for filtering querysets
            source_content_type = ContentType.objects.get_for_model(source)

            # Get check results and removed hosts
            check_results = source.get_check_results()
            removed_hosts = set(source.get_removed_hosts())

            # Create CheckResult objects and update or delete states
            for result in check_results:
                check_obj = CheckResult.from_dict(source, result)
                check_obj.save()
                state_kwargs = {
                    'source_type': source_content_type,
                    'source_id': source.pk,
                    'name': check_obj.name,
                    'host': check_obj.host,
                }
                if check_obj.host not in removed_hosts:
                    status = StateStatus.from_check_status(check_obj.status)
                    state_kwargs['defaults'] = {
                        'status': status,
                        'output': check_obj.output,
                        'metrics': check_obj.metrics,
                    }
                    State.objects.update_or_create(**state_kwargs)

            # Delete remaining removed hosts
            State.objects.filter(source_type=source_content_type,
                    source_id=source.pk, host__in=removed_hosts).delete()
