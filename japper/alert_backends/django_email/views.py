from vanilla import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy

from .forms import AlertSinkForm
from .models import AlertSink


class CreateAlertSink(CreateView):

    form_class = AlertSinkForm
    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')


class UpdateAlertSink(UpdateView):

    form_class = AlertSinkForm
    model = AlertSink
    success_url = reverse_lazy('monitoring_alert_sinks')

