from django.conf.urls import patterns, url

from .views import MonitoringSourcesList, StatesList


urlpatterns = patterns('',
    url(r'^sources/$', MonitoringSourcesList.as_view(),
        name='monitoring_sources'),
    url(r'^states/all/$', StatesList.as_view(), name='monitoring_states'),
    url(r'^states/problems/$', StatesList.as_view(problems_only=True),
        name='monitoring_states'),
)

