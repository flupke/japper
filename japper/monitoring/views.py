from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from vanilla import TemplateView, ListView, DetailView

from japper.views import BreadcrumbsMixin, JsonView
from .plugins import iter_monitoring_backends, iter_alert_backends
from .models import State, CheckResult
from .status import Status
from .forms import StatesSearchForm
from . import search


class MonitoringSourcesList(TemplateView):

    template_name = 'monitoring/sources_list.html'

    def get_context_data(self, **kwargs):
        return super(MonitoringSourcesList, self).get_context_data(
            backends=iter_monitoring_backends(),
            **kwargs
        )


class AlertSinksList(TemplateView):

    template_name = 'monitoring/alert_sinks_list.html'

    def get_context_data(self, **kwargs):
        return super(AlertSinksList, self).get_context_data(
            backends=iter_alert_backends(),
            **kwargs
        )


class StatesList(ListView):

    model = State
    paginate_by = 100
    context_object_name = 'states'
    problems_only = False
    form_class = StatesSearchForm

    def get_queryset(self):
        qs = super(StatesList, self).get_queryset()
        if self.problems_only:
            qs = qs.filter(status__in=Status.problems())
        qs = self.apply_search_filters(qs)
        return qs.order_by('host', 'name')

    def apply_search_filters(self, qs):
        form = StatesSearchForm(self.request.GET)
        if form.is_valid():
            qs = search.filter(qs, form.cleaned_data['q'])
        return qs

    def get_context_data(self, **kwargs):
        states_by_host = State.group_by_host(self.object_list)
        search_form = self.get_form(self.request.GET)
        return super(StatesList, self).get_context_data(
            states_by_host=states_by_host,
            Status=Status,
            problems_only=self.problems_only,
            search_form=search_form,
            **kwargs
        )


class StateDetail(BreadcrumbsMixin, DetailView):

    model = State
    context_object_name = 'state'

    def get_breadcrumbs(self):
        state = self.get_object()
        return [
            ('States', reverse_lazy('monitoring_all_states')),
            (state, None),
        ]


class StateHistory(BreadcrumbsMixin, DetailView):

    model = State
    paginate_by = 10
    template_name = 'monitoring/state_history.html'

    def get_breadcrumbs(self):
        state = self.get_object()
        return [
            ('States', reverse_lazy('monitoring_all_states')),
            (state, state.get_absolute_url()),
            ('History', None),
        ]

    def get_context_data(self, **kwargs):
        state = self.get_object()
        check_results = CheckResult.objects.get_state_log(state,
                                                          max_results=None)
        paginate_by = self.get_paginate_by()
        page = self.paginate_queryset(check_results, paginate_by)
        return super(StateHistory, self).get_context_data(
            page_obj=page,
            check_results=page.object_list,
            paginator=page.paginator,
            **kwargs
        )


class MuteState(JsonView):

    def post(self, request, pk):
        state = get_object_or_404(State, pk=pk)
        state.muted = not state.muted
        state.save()
        return {'muted': state.muted}
