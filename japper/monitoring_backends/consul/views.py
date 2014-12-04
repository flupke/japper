from vanilla import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from japper.views import BreadcrumbsMixin
from .forms import MonitoringSourceForm
from .models import MonitoringSource


class CreateMonitoringSource(BreadcrumbsMixin, CreateView):

    form_class = MonitoringSourceForm
    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')
    breadcrumbs = [
        ('Monitoring sources', reverse_lazy('monitoring_sources')),
        ('Create consul source', None),
    ]


class UpdateMonitoringSource(BreadcrumbsMixin, UpdateView):

    form_class = MonitoringSourceForm
    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')

    def get_breadcrumbs(self):
        source = self.get_object()
        return [
            ('Monitoring sources', reverse_lazy('monitoring_sources')),
            (source, None),
        ]


class DeleteMonitoringSource(BreadcrumbsMixin, DeleteView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')

    def get_breadcrumbs(self):
        source = self.get_object()
        return [
            ('Monitoring sources', reverse_lazy('monitoring_sources')),
            (source, source.get_absolute_url()),
            ('Delete', None),
        ]
