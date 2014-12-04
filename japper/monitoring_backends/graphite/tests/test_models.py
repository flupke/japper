import mock
from httmock import HTTMock

from japper.monitoring.status import Status
from ..client import GraphiteClient
from ..models import Check
from .test_client import build_json_response


def test_check_run():
    client = GraphiteClient('https://graphite.com')

    check = Check(target='metric.path', host='foo.com', name='check')
    with HTTMock(build_json_response([{'datapoints': [], 'target': 'foo'}])):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.unknown,
            'metrics': {},
            'output': 'got empty data for "metric.path"',
        }

    check = Check(target='metric.path', host='foo.com', name='check',
            critical_operator=Check.GT, critical_value=0)
    with HTTMock(build_json_response([{'datapoints': [[1, 1]], 'target': 'foo'}])):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.critical,
            'metrics': {'check': 1},
            'output': 'check critical',
        }

    check = Check(target='metric.path', host='foo.com', name='check',
            critical_operator=Check.LT, critical_value=0,
            warning_operator=Check.GT, warning_value=0)
    with HTTMock(build_json_response([{'datapoints': [[1, 1]], 'target': 'foo'}])):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.warning,
            'metrics': {'check': 1},
            'output': 'check warning',
        }

    check = Check(target='metric.path', host='foo.com', name='check',
            critical_operator=Check.LT, critical_value=0,
            warning_operator=Check.LT, warning_value=0)
    with HTTMock(build_json_response([{'datapoints': [[1, 1]], 'target': 'foo'}])):
        assert check.run(client) == {
            'name': 'check',
            'host': 'foo.com',
            'status': Status.passing,
            'metrics': {'check': 1},
            'output': 'check passing',
        }

    client = mock.Mock(spec=GraphiteClient)
    client.get_metric.side_effect = Exception('foo')
    assert check.run(client) == {
        'name': 'check',
        'host': 'foo.com',
        'status': Status.unknown,
        'metrics': {},
        'output': 'unexpected error: foo',
    }
