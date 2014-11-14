from django.conf import settings


EC2_DNS_NAMES_CACHE_TTL = getattr(settings,
        'JAPPER_CONSUL_EC2_DNS_NAMES_CACHE_TTL', 3600 * 24)
