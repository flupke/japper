import urlparse

from django.conf import settings


def build_absolute_uri(location):
    '''
    Same as :meth:`HttpRequest.build_absolute_uri`, but using the
    :attr:`SITE_URL` setting.
    '''
    return urlparse.urljoin(settings.SITE_URL, location)
