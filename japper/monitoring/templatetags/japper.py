from __future__ import absolute_import
from django import template

from japper.monitoring.search import build_search_url


register = template.Library()


@register.simple_tag(name='search')
def search(**kwargs):
    return build_search_url(**kwargs)
