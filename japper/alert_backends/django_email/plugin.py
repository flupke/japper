from japper.monitoring.plugins.backend import AlertBackend


class DjangoEmailBackend(AlertBackend):

    name = 'django-email'
    model = 'django_email.AlertSink'
    create_instance_view = 'django_email_create_alert_sink'


def create_backend():
    return DjangoEmailBackend()
