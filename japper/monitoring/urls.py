from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (MonitoringSourcesList, AlertSinksList, StatesList,
        StateDetail)


urlpatterns = patterns('',
    url(r'^sources/$', login_required(MonitoringSourcesList.as_view()),
        name='monitoring_sources'),
    url(r'^alert-sinks/$', login_required(AlertSinksList.as_view()),
        name='monitoring_alert_sinks'),
    url(r'^states/all/$', login_required(StatesList.as_view()),
        name='monitoring_all_states'),
    url(r'^states/problems/$',
        login_required(StatesList.as_view(problems_only=True)),
        name='monitoring_problems'),
    url(r'states/(?P<pk>\d+)/$', login_required(StateDetail.as_view()),
        name='monitoring_state_detail'),
)
