import json
import logging
from urlparse import urljoin
import random

import requests
import six

from .exceptions import NoServerFound


logger = logging.getLogger(__name__)


class Client(object):
    '''
    An interface to the Consul agent HTTP API

    *servers* is the consul HTTP API URL, it can be a string or a list of
    strings, in which case requests will be load-balanced between the given
    servers.
    '''

    def __init__(self, servers, timeout=3, max_retries=3):
        self.timeout = timeout
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
        # Setup requests session
        self.session = requests.Session()
        self.session.mount('http://',
                requests.adapters.HTTPAdapter(max_retries=max_retries))
        self.session.mount('https://',
                requests.adapters.HTTPAdapter(max_retries=max_retries))

    def request(self, method, path, data=None, params=None):
        local_servers = self.local_servers[:]
        remote_servers = self.remote_servers[:]
        random.shuffle(local_servers)
        random.shuffle(remote_servers)
        servers = local_servers + remote_servers
        for base_url in servers:
            url = urljoin(base_url, path)
            try:
                response = self.session.request(method, url,
                        data=json.dumps(data), params=params,
                        timeout=self.timeout)
                response.raise_for_status()
                break
            except requests.RequestException:
                logger.warning('consul request failed on %s', url,
                        exc_info=True)
        else:
            error_fmt = 'all consul servers are offline: %s'
            error_args = ', '.join(servers)
            logger.error(error_fmt, error_args)
            raise NoServerFound(error_fmt % error_args)
        return response


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
