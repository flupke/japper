from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (CreateMonitoringSource, UpdateMonitoringSource,
        DeleteMonitoringSource)


urlpatterns = patterns('',
    url(r'^monitoring-source/create/$',
        login_required(CreateMonitoringSource.as_view()),
        name='graphite_create_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/$',
        login_required(UpdateMonitoringSource.as_view()),
        name='graphite_update_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/delete/$',
        login_required(DeleteMonitoringSource.as_view()),
        name='graphite_delete_monitoring_source'),
)
