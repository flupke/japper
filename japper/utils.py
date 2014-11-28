import urlparse

import requests

from django.conf import settings


def build_absolute_uri(location):
    '''
    Same as :meth:`HttpRequest.build_absolute_uri`, but using the
    :attr:`SITE_URL` setting.
    '''
    return urlparse.urljoin(settings.SITE_URL, location)


class HttpClient(object):
    '''
    A generic base class for HTTP clients, with retries and timeouts.
    '''

    def __init__(self, timeout=3, max_retries=3):
        self.timeout = timeout
        # Setup requests session
        self.session = requests.Session()
        self.session.mount('http://',
                requests.adapters.HTTPAdapter(max_retries=max_retries))
        self.session.mount('https://',
                requests.adapters.HTTPAdapter(max_retries=max_retries))

    def request(self, method, url, data=None, params=None,
            raise_for_status=True):
        response = self.session.request(method, url, data=data, params=params,
                timeout=self.timeout)
        if raise_for_status:
            response.raise_for_status()
        return response

    def get(self, url, data=None, params=None, raise_for_status=True):
        return self.request('GET', url, data=data, params=params,
                raise_for_status=raise_for_status)

    def post(self, url, data=None, params=None, raise_for_status=True):
        return self.request('POST', url, data=data, params=params,
                raise_for_status=raise_for_status)
