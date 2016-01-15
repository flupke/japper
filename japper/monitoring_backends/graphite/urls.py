from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (CreateMonitoringSource, UpdateMonitoringSource,
                    DeleteMonitoringSource, ChecksList, CreateCheck,
                    UpdateCheck, DeleteCheck)


urlpatterns = patterns(
    '',
    url(r'^monitoring-source/create/$',
        login_required(CreateMonitoringSource.as_view()),
        name='graphite_create_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/$',
        login_required(UpdateMonitoringSource.as_view()),
        name='graphite_update_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/delete/$',
        login_required(DeleteMonitoringSource.as_view()),
        name='graphite_delete_monitoring_source'),
    url(r'^monitoring-source/(?P<pk>\d+)/checks/$',
        login_required(ChecksList.as_view()),
        name='graphite_checks'),
    url(r'^monitoring-source/(?P<source_pk>\d+)/create-check/$',
        login_required(CreateCheck.as_view()),
        name='graphite_create_check'),
    url(r'^checks/(?P<pk>\d+)/$',
        login_required(UpdateCheck.as_view()),
        name='graphite_update_check'),
    url(r'^checks/(?P<pk>\d+)/delete/$',
        login_required(DeleteCheck.as_view()),
        name='graphite_delete_check'),
)
