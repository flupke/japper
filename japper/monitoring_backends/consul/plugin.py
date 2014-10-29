from japper.monitoring.plugins.monitoring_backend import MonitoringBackend


class ConsulBackend(MonitoringBackend):

    name = 'consul'
    monitoring_source_model = 'consul.MonitoringSource'
    create_source_view = 'consul_create_monitoring_source'


def create_backend():
    return ConsulBackend()
