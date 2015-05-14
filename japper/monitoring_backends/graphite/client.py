from urlparse import urljoin
import logging
import datetime

from japper.utils import HttpClient
from .exceptions import InvalidDataFormat, EmptyData
from . import settings


logger = logging.getLogger(__name__)


def average(values):
    return float(sum(values)) / len(values)


class GraphiteClient(HttpClient):

    def __init__(self, endpoint, *args, **kwargs):
        super(GraphiteClient, self).__init__(*args, **kwargs)
        self.endpoint = endpoint

    def get_metric(self, target, from_=60, aggregator=average):
        '''
        Get the current value of a metric, by aggregating values from Graphite
        over an interval.

        Values returned by *target* over the period *from_* are aggregated
        using the *aggregator* function, *from_* being in seconds from the most
        recent data point.

        Returns the resulting floating point value, or raise an
        :class:`InvalidDataFormat` exception if the retured data is invalid.
        '''
        query_from = max(settings.MINIMUM_QUERIES_RANGE, from_)
        url = urljoin(self.endpoint, '/render')
        response = self.get(url, params={
            'target': target,
            'format': 'json',
            'from': '-%ss' % query_from,
        })
        data = response.json()

        # Check data format
        err_prefix = 'got invalid data for "%s": ' % target
        if not isinstance(data, list):
            raise InvalidDataFormat(err_prefix +
                    'expected a list but got a %s instead' % type(data))
        if not len(data):
            err_message = err_prefix + 'empty data returned'
            raise InvalidDataFormat(err_message)
        if len(data) > 1:
            err_message = err_prefix + 'multiple metrics returned'
            raise InvalidDataFormat(err_message)
        if not isinstance(data[0], dict):
            raise InvalidDataFormat(err_prefix + 'expected a dict '
                    'at item 0 but got a %s instead' % type(data[0]))

        # Filter data, removing null points and trimming to the desired range
        values = filter_values(data[0]['datapoints'], from_)
        if not values:
            raise EmptyData('got no valid data points for "%s"' % target)

        # Aggregate values
        return aggregator(values)


def filter_values(datapoints, max_age):
    '''
    Filter and extract values from raw Graphite *datapoints*.

    Keeps non-null values and with a maximum delta of *max_age* seconds from
    the most recent data point.
    '''
    # Convert timestamps and filter out null values
    datapoints = [(e[0], datetime.datetime.fromtimestamp(e[1]))
        for e in datapoints if e[0] is not None]
    if not len(datapoints):
        return []
    last_point_date = datapoints[-1][1]
    datapoints = filter(
        lambda (_, date): (last_point_date - date).total_seconds() <= max_age,
        datapoints)
    return [e[0] for e in datapoints]
