import json
import logging
from urlparse import urljoin
import random

import requests
import six

from japper.utils import HttpClient
from .exceptions import NoServerFound


logger = logging.getLogger(__name__)


class ConsulClient(HttpClient):
    '''
    An interface to the Consul agent HTTP API

    *servers* is the consul HTTP API base URL. It can be a string, or a list of
    strings. In the latter case requests will be load-balanced between the
    given servers.
    '''

    def __init__(self, servers, *args, **kwargs):
        super(ConsulClient, self).__init__(*args, **kwargs)
        # Separate local and remote servers
        if isinstance(servers, six.string_types):
            servers = [servers]
        self.local_servers = []
        self.remote_servers = []
        for server in servers:
            if 'localhost' in server or '127.0.0.1' in server:
                self.local_servers.append(server)
            else:
                self.remote_servers.append(server)

    def request(self, method, path, data=None, params=None,
                raise_for_status=True):
        local_servers = self.local_servers[:]
        remote_servers = self.remote_servers[:]
        random.shuffle(local_servers)
        random.shuffle(remote_servers)
        servers = local_servers + remote_servers
        for base_url in servers:
            url = urljoin(base_url, path)
            try:
                response = super(ConsulClient, self).request(
                    method,
                    url,
                    data=json.dumps(data),
                    params=params
                )
                break
            except requests.RequestException:
                logger.warning('consul request failed on %s', url,
                               exc_info=True)
        else:
            error_fmt = 'all consul servers are offline: %s'
            error_args = ', '.join(servers)
            logger.error(error_fmt, error_args)
            raise NoServerFound(error_fmt % error_args)
        return response.json()


def parse_nagios_output(value):
    '''
    Extract text and metrics from a nagios-formatted output.

    Return a tuple containing (text, metrics). For example the following
    output::

        OK | 'cpu'=4 'gpu'=8

    Would give ``('OK', {'cpu': 4, 'gpu': 8})``
    '''
    text, _, perfdata = value.partition('|')
    text = text.strip().rstrip('\\')
    perfdata = perfdata.strip().rstrip('\\')
    metrics = {}
    for perfdata_item in perfdata.split():
        perfdata_name, _, perfdata_value = perfdata_item.partition('=')
        perfdata_name = perfdata_name.strip("'")
        perfdata_value = perfdata_value.partition(';')[0]
        try:
            perfdata_value = int(perfdata_value)
        except ValueError:
            try:
                perfdata_value = float(perfdata_value)
            except ValueError:
                pass
        metrics[perfdata_name] = perfdata_value
    return text, metrics
