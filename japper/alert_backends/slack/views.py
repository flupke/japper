from vanilla import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from japper.views import BreadcrumbsMixin
from .models import AlertSink


class CreateAlertSink(BreadcrumbsMixin, CreateView):

    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')
    breadcrumbs = [
        ('Alert sinks', reverse_lazy('monitoring_alert_sinks')),
        ('Create slack alert sink', None),
    ]


class UpdateAlertSink(BreadcrumbsMixin, UpdateView):

    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')

    def get_breadcrumbs(self):
        sink = self.get_object()
        return [
            ('Alert sinks', reverse_lazy('monitoring_alert_sinks')),
            (sink, None),
        ]


class DeleteAlertSink(BreadcrumbsMixin, DeleteView):

    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')

    def get_breadcrumbs(self):
        sink = self.get_object()
        return [
            ('Alert sinks', reverse_lazy('monitoring_alert_sinks')),
            (sink, sink.get_absolute_url()),
            ('Delete', None),
        ]
