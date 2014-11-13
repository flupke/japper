from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from japper.monitoring.plugins import get_url_patterns


urlpatterns = get_url_patterns('',
    url(r'^$', RedirectView.as_view(pattern_name='monitoring_problems'),
        name='frontpage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitoring/', include('japper.monitoring.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^users/', include('japper.users.urls')),
)
