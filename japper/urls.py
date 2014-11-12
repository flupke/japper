from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from japper.monitoring.views import StatesList


urlpatterns = patterns('',
    url(r'^$',login_required(StatesList.as_view(problems_only=True)),
        name='frontpage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitoring/', include('japper.monitoring.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^users/', include('japper.users.urls')),
)
