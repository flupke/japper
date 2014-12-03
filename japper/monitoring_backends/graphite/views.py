from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from vanilla import CreateView, UpdateView, DeleteView, DetailView

from .models import MonitoringSource, Check


class CreateMonitoringSource(CreateView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')


class UpdateMonitoringSource(UpdateView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')


class DeleteMonitoringSource(DeleteView):

    model = MonitoringSource
    success_url = reverse_lazy('monitoring_sources')


class ChecksList(DetailView):

    model = MonitoringSource
    context_object_name = 'source'
    template_name = 'graphite/check_list.html'

    def get_context_data(self, **kwargs):
        source = self.get_object()
        return super(ChecksList, self).get_context_data(
                checks=source.checks.all(), **kwargs)


class CheckCRUDViewMixin(object):

    def get_success_url(self):
        check = self.object
        return reverse('graphite_checks', kwargs={'pk': check.source.pk})


class CreateCheck(CheckCRUDViewMixin, CreateView):

    model = Check

    def form_valid(self, form):
        self.object = form.save(commit=False)
        source = MonitoringSource.objects.get(pk=self.kwargs['source_pk'])
        self.object.source = source
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class UpdateCheck(CheckCRUDViewMixin, UpdateView):

    model = Check


class DeleteCheck(CheckCRUDViewMixin, DeleteView):

    model = Check
