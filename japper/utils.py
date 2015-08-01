import urlparse
import functools
import logging

import requests
from raven.contrib.django.raven_compat.models import client as raven_client
from django_redis import get_redis_connection
from redis_lock import Lock
from django.conf import settings


logger = logging.getLogger(__name__)


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


def report_to_sentry(func):
    '''
    A decorator to report errors to sentry.
    '''

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            raven_client.captureException()
            raise

    return wrapper


def single_instance(expire=60*3):
    '''
    A decorator that can be used to make sure only one instance of a function
    is running at the same time.

    If another instance of the function is running, the function is not
    executed.

    If *expire* is given, the lock is automatically cleaned up after this
    amount of seconds. The default is 3 minutes.
    '''

    def decorator(func):
        func_path = '%s.%s' % (func.__module__, func.__name__)
        lock_name = 'japper:utils:single_instance:%s' % func_path

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client = get_redis_connection()
            lock = Lock(client, lock_name, expire=expire)
            try:
                if lock.acquire(blocking=False):
                    return func(*args, **kwargs)
                else:
                    logger.warning('another instance of %s is running',
                            func_path)
            finally:
                lock.release()

        return wrapper

    return decorator

