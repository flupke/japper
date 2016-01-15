from django.conf import settings


# Sometimes graphite returns empty lists when querying too small ranges (not
# empty datapoints, just an empty list [] response, which does not seem
# normal...) , so we query at least this amount of data and just take the
# interval that interest us in it.
MINIMUM_QUERIES_RANGE = getattr(settings, 'GRAPHITE_MINIMUM_QUERIES_RANGE',
                                60 * 10)
