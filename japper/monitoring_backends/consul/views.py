from vanilla import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy

from .forms import MonitoringSourceForm
from .models import MonitoringSource


class CreateMonitoringSource(CreateView):

    form_class = MonitoringSourceForm
    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')


class UpdateMonitoringSource(UpdateView):

    form_class = MonitoringSourceForm
    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')
