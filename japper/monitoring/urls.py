from django.conf.urls import patterns, url

from .views import MonitoringSourcesList, StatesList


urlpatterns = patterns('',
    url(r'^sources/$', MonitoringSourcesList.as_view(),
        name='monitoring_sources'),
    url(r'^states/$', StatesList.as_view(), name='monitoring_states'),
)

