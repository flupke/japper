from django.conf import settings


FROM_EMAIL = getattr(settings, 'JAPPER_FROM_EMAIL', 'japper@example.com')
