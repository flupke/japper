from vanilla import TemplateView

from .plugins import iter_monitoring_backends


class MonitoringSourcesList(TemplateView):

    template_name = 'monitoring/sources_list.html'

    def get_context_data(self, **kwargs):
        return super(MonitoringSourcesList, self).get_context_data(
                backends=iter_monitoring_backends(), **kwargs)
