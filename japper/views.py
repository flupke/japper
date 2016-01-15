import json

from django.http import HttpResponse
from vanilla import View


class BreadcrumbsMixin(object):
    '''
    Mixin for views that define breadcrumbs.

    The :attr:`breadcrumbs` class attribute should be a list of (label, url)
    pairs. :meth:`get_breadcrumbs` can also be reimplemented to generate
    dynamic breadcrumbs.
    '''

    breadcrumbs = []

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_context_data(self, **kwargs):
        return super(BreadcrumbsMixin, self).get_context_data(
            breadcrumbs=self.get_breadcrumbs(), **kwargs)


class JsonView(View):

    def dispatch(self, *args, **kwargs):
        response = super(JsonView, self).dispatch(*args, **kwargs)
        if not isinstance(response, HttpResponse):
            response = HttpResponse(json.dumps(response),
                                    content_type='application/json')
        return response
