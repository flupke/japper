from httmock import HTTMock

from japper.monitoring.status import Status
from ..client import GraphiteClient
from ..models import Check
from .test_client import build_json_response, SINGLE_METRIC_DATA


def test_check_run():
    client = GraphiteClient('https://graphite.com')
    check = Check(target='metric.path', host='foo.com', name='check', )

    with HTTMock(build_json_response([{'datapoints': [], 'target': 'foo'}])):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.unknown,
            'metrics': {},
            'output': 'got empty data for "metric.path"',
        }

    with HTTMock(build_json_response(SINGLE_METRIC_DATA)):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.passing,
            'metrics': {'check': 577.5714168122989},
            'output': 'check passing',
        }
