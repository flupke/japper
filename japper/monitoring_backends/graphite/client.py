from urlparse import urljoin
import logging

from japper.utils import HttpClient
from .exceptions import InvalidDataFormat, EmptyData


logger = logging.getLogger(__name__)


def average(values):
    return float(sum(values)) / len(values)


class GraphiteClient(HttpClient):

    def __init__(self, endpoint, *args, **kwargs):
        super(GraphiteClient, self).__init__(*args, **kwargs)
        self.endpoint = endpoint

    def get_metric(self, target, from_='-1minutes', aggregator=average):
        '''
        Get the current value of a metric, by aggregating values from Graphite
        over an interval.

        Values returned by *target* over the period *from_* are aggregated
        using the *aggregator* function.

        Returns the resulting floating point value, or raise an
        :class:`InvalidDataFormat` exception if the retured data is invalid.
        '''
        url = urljoin(self.endpoint, '/render')
        response = self.get(url, params={
            'target': target,
            'format': 'json',
            'from': from_,
        })
        data = response.json()

        # Check data format
        err_prefix = 'got invalid data for "%s": ' % target
        if not isinstance(data, list):
            raise InvalidDataFormat(err_prefix +
                    'expected a list but got a %s instead' % type(data))
        if not len(data):
            err_message = err_prefix + 'null data returned'
            raise InvalidDataFormat(err_message)
        if len(data) > 1:
            err_message = err_prefix + 'multiple metrics returned'
            raise InvalidDataFormat(err_message)
        if not isinstance(data[0], dict):
            raise InvalidDataFormat(err_prefix + 'expected a dict '
                    'at item 0 but got a %s instead' % type(data[0]))

        # Extract values
        values = [e[0] for e in data[0]['datapoints'] if e[0] is not None]
        if not values:
            raise EmptyData('got empty data for "%s"' % target)

        # Aggregate values
        return aggregator(values)
