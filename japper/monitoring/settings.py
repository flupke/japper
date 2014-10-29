from django.conf import settings


# Minimum number of identical consecutive check result statuses needed to
# change the status of a state
MIN_CONSECUTIVE_STATUSES = getattr(settings,
        'MONITORING_MIN_CONSECUTIVE_STATUSES', 3)
