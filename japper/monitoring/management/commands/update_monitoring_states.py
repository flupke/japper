from django.core.management.base import BaseCommand, CommandError
from japper.monitoring.tasks import update_monitoring_states


class Command(BaseCommand):

    help = 'Update monitoring states (for debugging)'

    def handle(self, *args, **options):
        update_monitoring_states.run()
