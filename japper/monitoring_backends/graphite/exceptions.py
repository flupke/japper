from japper.monitoring.exceptions import JapperMonitoringException


class GraphiteException(JapperMonitoringException):
    pass

class InvalidDataFormat(GraphiteException):
    pass
