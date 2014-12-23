from django.core.management.base import BaseCommand
import django.conf

from japper.monitoring.tasks import fetch_check_results


class Command(BaseCommand):

    help = 'Update states once'

    def handle(self, *args, **options):
        django.conf.settings.CELERY_ALWAYS_EAGER = True
        fetch_check_results.delay()
