from vanilla import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from japper.views import BreadcrumbsMixin
from .forms import AlertSinkForm
from .models import AlertSink


class CreateAlertSink(BreadcrumbsMixin, CreateView):

    form_class = AlertSinkForm
    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')
    breadcrumbs = [
        ('Alert sinks', reverse_lazy('monitoring_alert_sinks')),
        ('Create django-email alert sink', None),
    ]


class UpdateAlertSink(BreadcrumbsMixin, UpdateView):

    form_class = AlertSinkForm
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
