from vanilla import TemplateView, ListView

from .plugins import iter_monitoring_backends
from .models import State


class MonitoringSourcesList(TemplateView):

    template_name = 'monitoring/sources_list.html'

    def get_context_data(self, **kwargs):
        return super(MonitoringSourcesList, self).get_context_data(
                backends=iter_monitoring_backends(), **kwargs)


class StatesList(ListView):

    model = State
    paginate_by = 100
    context_object_name = 'states'
