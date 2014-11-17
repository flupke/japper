import shlex

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from .status import Status
from .plugins import iter_monitoring_backends


_registry = {}


def register_tag(name, filter_func):
    if name in _registry:
        raise ValueError('cannot register search filter func %s, name %s '
                'is already used by %s' % (filter_func, name, _registry[name]))
    _registry[name] = filter_func


def filter(qs, search_text):
    '''
    Filter queryset object *qs* with *search_text*.
    '''
    tokens = shlex.split(search_text)
    query = Q()
    for token in tokens:
        if ':' in token:
            tag, _, value = token.partition(':')
        else:
            tag = None
            value = token
        try:
            filter_func = _registry[tag]
        except KeyError:
            q = filter_by_any(value)
        else:
            q = filter_func(value)
        query &= q
    return qs.filter(query)


def filter_by_name(value):
    return Q(name__icontains=value)


def filter_by_host(value):
    return Q(host__icontains=value)


def filter_by_status(value):
    try:
        status = Status.from_string(value.lower())
    except ValueError:
        return Q()
    return Q(status=status)


def filter_by_any(value):
    query = Q()
    for tag_name, filter_func in _registry.items():
        if tag_name is not None:
            query |= filter_func(value)
    return query


def filter_by_source(value):
    '''
    Filter by monitoring source.

    *value* may be a simple string, in which case all backend instances with
    this name are matched, or a "backend_name/instance_name" string to target a
    single backend.
    '''
    if ':' in value:
        backend_name, _, source_name = value.partition(':')
        for backend in iter_monitoring_backends():
            if backend.get_name() == backend_name:
                break
        else:
            backend = None
    else:
        backend = None
        source_name = value
    if backend is None:
        query = Q()
        for backend in iter_monitoring_backends():
            query |= filter_by_backend(backend, source_name)
    else:
        query = filter_by_backend(backend, source_name)
    return query


def filter_by_backend(backend, source_name):
    qs = backend.get_instances()
    try:
        backend_instance = qs.get(name=source_name)
    except ObjectDoesNotExist:
        return Q()
    source_type = ContentType.objects.get_for_model(
            backend_instance)
    return Q(source_type=source_type, source_id=backend_instance.pk)


register_tag('name', filter_by_name)
register_tag('host', filter_by_host)
register_tag('status', filter_by_status)
register_tag('source', filter_by_source)
register_tag(None, filter_by_any)
