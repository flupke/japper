from japper.monitoring.plugins.backend import MonitoringBackend


class GraphiteBackend(MonitoringBackend):

    name = 'graphite'
    model = 'graphite.MonitoringSource'
    create_instance_view = 'graphite_create_monitoring_source'


def create_backend():
    return GraphiteBackend()
