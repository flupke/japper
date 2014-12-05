from japper.monitoring.plugins.backend import AlertBackend


class SlackBackend(AlertBackend):

    name = 'slack'
    model = 'slack.AlertSink'
    create_instance_view = 'slack_create_alert_sink'


def create_backend():
    return SlackBackend()
