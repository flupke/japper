from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from vanilla import CreateView, UpdateView, DeleteView, DetailView
from robgracli import GraphiteClient
from robgracli.exceptions import BadResponse

from japper.views import BreadcrumbsMixin, JsonView
from .models import MonitoringSource, Check


class CreateMonitoringSource(BreadcrumbsMixin, CreateView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')
    breadcrumbs = [
        ('Monitoring sources', reverse_lazy('monitoring_sources')),
        ('Create graphite source', None),
    ]


class UpdateMonitoringSource(BreadcrumbsMixin, UpdateView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')

    def get_breadcrumbs(self):
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            (self.get_object(), None),
        ]


class DeleteMonitoringSource(BreadcrumbsMixin, DeleteView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')

    def get_breadcrumbs(self):
        source = self.get_object()
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            (source, source.get_absolute_url()),
            ('Delete', None),
        ]


class ChecksList(BreadcrumbsMixin, DetailView):

    model = MonitoringSource
    context_object_name = 'source'
    template_name = 'graphite/check_list.html'

    def get_breadcrumbs(self):
        source = self.get_object()
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            ('%s checks' % source, None),
        ]

    def get_context_data(self, **kwargs):
        source = self.get_object()
        return super(ChecksList, self).get_context_data(
            checks=source.checks.all(), **kwargs)


class CheckCRUDViewMixin(object):

    def get_success_url(self):
        check = self.object
        return reverse('graphite_checks', kwargs={'pk': check.source.pk})

    def get_context_data(self, **kwargs):
        if 'source' not in kwargs:
            kwargs['source'] = self.get_object().source
        return super(CheckCRUDViewMixin, self).get_context_data(**kwargs)


class CreateCheck(CheckCRUDViewMixin, BreadcrumbsMixin, CreateView):

    model = Check

    def get_source(self):
        return MonitoringSource.objects.get(pk=self.kwargs['source_pk'])

    def get_breadcrumbs(self):
        source = self.get_source()
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            ('%s checks' % source,
                reverse('graphite_checks', kwargs={'pk': source.pk})),
            ('Create check', None),
        ]

    def get_context_data(self, **kwargs):
        if 'source' not in kwargs:
            kwargs['source'] = self.get_source()
        return super(CreateCheck, self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        source = self.get_source()
        self.object.source = source
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class UpdateCheck(CheckCRUDViewMixin, BreadcrumbsMixin, UpdateView):

    model = Check

    def get_breadcrumbs(self):
        check = self.get_object()
        source = check.source
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            ('%s checks' % source,
                reverse('graphite_checks', kwargs={'pk': source.pk})),
            (check, None),
        ]


class DeleteCheck(CheckCRUDViewMixin, BreadcrumbsMixin, DeleteView):

    model = Check

    def get_breadcrumbs(self):
        check = self.get_object()
        source = check.source
        return [
            ('Monitoring sources', reverse('monitoring_sources')),
            ('%s checks' % source,
                reverse('graphite_checks', kwargs={'pk': source.pk})),
            (check, check.get_absolute_url()),
            ('Delete', None),
        ]


class GraphiteQueryPreview(JsonView):
    '''
    Used to dynamically preview graphite queries result.
    '''

    def get(self, request):
        endpoint = request.GET['endpoint']
        query = request.GET['query']
        client = GraphiteClient(endpoint)
        try:
            result = client.aggregate(query)
        except BadResponse as exc:
            return {
                'status': 'error',
                'error': exc.response.text,
                'error_type': 'html',
            }
        except Exception as exc:
            return {
                'status': 'error',
                'error': unicode(exc),
                'error_type': 'text',
            }
        return {
            'status': 'ok',
            'result': result,
        }
