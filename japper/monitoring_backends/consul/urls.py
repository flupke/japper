from django.conf.urls import patterns, url

from .views import CreateMonitoringSource, UpdateMonitoringSource


urlpatterns = patterns('',
    url(r'^monitoring-source/create/$', CreateMonitoringSource.as_view(),
        name='consul_create_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/$', UpdateMonitoringSource.as_view(),
        name='consul_update_monitoring_source'),
)
