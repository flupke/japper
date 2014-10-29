from collections import Counter

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

        def host_group_data(host, states):
            status_counter = Counter()
            for state in states:
                status_counter[state.status.name] += 1
            return (host, states, status_counter)

        # Group states by host
        prev_host = no_host = object()
        host_states = []
        states_by_host = []
        for state in self.get_queryset():
            if prev_host != no_host and state.host != prev_host:
                states_by_host.append(host_group_data(prev_host, host_states))
                host_states = []
            host_states.append(state)
            prev_host = state.host
        if host_states:
            states_by_host.append(host_group_data(prev_host, host_states))

        return super(StatesList, self).get_context_data(
                states_by_host=states_by_host, StateStatus=StateStatus,
                **kwargs)

