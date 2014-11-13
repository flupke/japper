from vanilla import TemplateView, ListView, DetailView

from .plugins import iter_monitoring_backends, iter_alert_backends
from .models import State, CheckResult
from .status import Status


class MonitoringSourcesList(TemplateView):

    template_name = 'monitoring/sources_list.html'

    def get_context_data(self, **kwargs):
        return super(MonitoringSourcesList, self).get_context_data(
                backends=iter_monitoring_backends(), **kwargs)


class AlertSinksList(TemplateView):

    template_name = 'monitoring/alert_sinks_list.html'

    def get_context_data(self, **kwargs):
        return super(AlertSinksList, self).get_context_data(
                backends=iter_alert_backends(), **kwargs)


class StatesList(ListView):

    model = State
    paginate_by = 100
    context_object_name = 'states'
    problems_only = False

    def get_queryset(self):
        qs = super(StatesList, self).get_queryset()
        if self.problems_only:
            qs = qs.filter(status__in=Status.problems())
        qs = self.apply_get_params_filters(qs)
        return qs.order_by('host', 'name')

    def apply_get_params_filters(self, qs):
        params = self.request.GET.dict()
        if 'status' in params:
            params['status'] = Status.from_string(params['status'])
        params.pop('page', None)
        return qs.filter(**params)

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        paginate_by = self.get_paginate_by()
        page = self.paginate_queryset(queryset, paginate_by)
        states_by_host = State.group_by_host(page.object_list)
        return super(StatesList, self).get_context_data(
                states_by_host=states_by_host,
                Status=Status,
                problems_only=self.problems_only,
                **kwargs)


class StateDetail(DetailView):

    model = State
    context_object_name = 'state'


class StateHistory(DetailView):

    model = State
    paginate_by = 10
    template_name = 'monitoring/state_history.html'

    def get_context_data(self, **kwargs):
        state = self.get_object()
        check_results = CheckResult.objects.get_state_log(state, max_results=None)
        paginate_by = self.get_paginate_by()
        page = self.paginate_queryset(check_results, paginate_by)
        return super(StateHistory, self).get_context_data(page_obj=page,
                check_results=page.object_list, paginator=page.paginator,
                **kwargs)
