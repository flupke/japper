import mock
from httmock import HTTMock
from robgracli import GraphiteClient
from robgracli.exceptions import GraphiteException
import pytest
from django.utils import timezone

from japper.monitoring.models import State
from japper.monitoring.status import Status
from ..models import Check, MonitoringSource
from .utils import build_json_response


@pytest.mark.django_db
def test_check_run():
    client = GraphiteClient('https://graphite.com')
    source = MonitoringSource.objects.create()
    now = timezone.now()
    State.objects.create(source=source, host='foo.com', status=Status.passing,
                         last_checked=now)

    check = Check(query='metric.path', host='foo.com', name='check')
    with HTTMock(build_json_response([{'datapoints': [], 'target': 'foo'}])):
        assert check.run(source, client) == [{
            'name': 'check',
            'host': 'foo.com',
            'status': Status.unknown,
            'metrics': {},
            'output': 'got no valid data points for "check"',
        }]

    check = Check(query='metric.path', host='foo.com', name='check',
                  critical_operator=Check.GT, critical_value=0)
    response_data = [{'datapoints': [[1, 1]], 'target': 'foo'}]
    with HTTMock(build_json_response(response_data)):
        assert check.run(source, client) == [{
            'name': 'check',
            'host': 'foo.com',
            'status': Status.critical,
            'metrics': {'check': 1},
            'output': 'critical - check > 0 (1.0)',
        }]

    check = Check(query='metric.path', host='foo.com', name='check',
                  critical_operator=Check.LT, critical_value=0,
                  warning_operator=Check.GT, warning_value=0)
    response_data = [{'datapoints': [[1, 1]], 'target': 'foo'}]
    with HTTMock(build_json_response(response_data)):
        assert check.run(source, client) == [{
            'name': 'check',
            'host': 'foo.com',
            'status': Status.warning,
            'metrics': {'check': 1},
            'output': 'warning - check > 0 (1.0)',
        }]

    check = Check(query='metric.path', host='foo.com', name='check',
                  critical_operator=Check.LT, critical_value=0,
                  warning_operator=Check.LT, warning_value=0)
    response_data = [{'datapoints': [[1, 1]], 'target': 'foo'}]
    with HTTMock(build_json_response(response_data)):
        assert check.run(source, client) == [{
            'name': 'check',
            'host': 'foo.com',
            'status': Status.passing,
            'metrics': {'check': 1},
            'output': 'passing - check = 1.0',
        }]

    client = mock.Mock(spec=GraphiteClient)
    client.aggregate.side_effect = GraphiteException('foo')
    assert check.run(source, client) == [{
        'name': 'check',
        'host': 'foo.com',
        'status': Status.unknown,
        'metrics': {},
        'output': 'unexpected error: foo',
    }]
