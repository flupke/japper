import json

import pytest
from httmock import all_requests, HTTMock

from ..client import GraphiteClient
from ..exceptions import InvalidDataFormat


SINGLE_METRIC_DATA = [{
    'datapoints': [
        [524.9439252336449, 1417629030],
        [625.8536585365854, 1417629040],
        [581.9166666666666, 1417629050],
    ],
    'target': 'foo'
}]
MULTI_METRIC_DATA = [SINGLE_METRIC_DATA[0], SINGLE_METRIC_DATA[0]]


def build_json_response(data):
    @all_requests
    def json_response(url, request):
        return {
            'status_code': 200,
            'content': json.dumps(data)
        }
    return json_response


def test_data_format_check():
    client = GraphiteClient('https://graphite.com')

    # Empty response
    with HTTMock(build_json_response([])):
        with pytest.raises(InvalidDataFormat):
            client.get_metric('metric.path')

    # Multiple metrics
    with HTTMock(build_json_response(MULTI_METRIC_DATA)):
        with pytest.raises(InvalidDataFormat):
            client.get_metric('metric.path')


def test_aggregators():
    client = GraphiteClient('https://graphite.com')
    with HTTMock(build_json_response(SINGLE_METRIC_DATA)):
        assert client.get_metric('metric.path') == 577.5714168122989
        assert client.get_metric('metric.path', aggregator=max) == 625.8536585365854
        assert client.get_metric('metric.path', aggregator=min) == 524.9439252336449
