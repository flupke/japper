
from vanilla import TemplateView, ListView

from .plugins import iter_monitoring_backends
from .models import State, StateStatus


class MonitoringSourcesList(TemplateView):

    template_name = 'monitoring/sources_list.html'

    def get_context_data(self, **kwargs):
        return super(MonitoringSourcesList, self).get_context_data(
                backends=iter_monitoring_backends(), **kwargs)


class StatesList(ListView):

    model = State
    paginate_by = 100
    context_object_name = 'states'

    def get_queryset(self):
        qs = super(StatesList, self).get_queryset()
        return qs.order_by('host', 'name')

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by()
        page = self.paginate_queryset(queryset, paginate_by)
        states_by_host = State.group_by_host(page.object_list)
        return super(StatesList, self).get_context_data(
                states_by_host=states_by_host, StateStatus=StateStatus,
                **kwargs)

