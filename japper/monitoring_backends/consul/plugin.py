from japper.monitoring.plugins.backend import MonitoringBackend


class ConsulBackend(MonitoringBackend):

    name = 'consul'
    model = 'consul.MonitoringSource'
    create_instance_view = 'consul_create_monitoring_source'


def create_backend():
    return ConsulBackend()
