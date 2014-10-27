from django.conf.urls import patterns, url

from .views import MonitoringSourcesList


urlpatterns = patterns('',
    url(r'^sources/$', MonitoringSourcesList.as_view(),
        name='monitoring_sources'),
)

