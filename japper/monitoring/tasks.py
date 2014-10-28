from celery import shared_task

from .models import CheckResult
from .plugins import iter_monitoring_backends


@shared_task
def get_check_results():
    '''
    Cron job fetching all check results from registered backends and inserting
    them in the database.
    '''
    for backend in iter_monitoring_backends():
        for source in backend.get_monitoring_sources(active=True):
            for result in source.get_check_results():
                obj = CheckResult.from_dict(source, result)
                obj.save()
