from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from japper.monitoring.plugins import get_url_patterns


urlpatterns = get_url_patterns('',
    # Examples:
    # url(r'^$', 'japper.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitoring/', include('japper.monitoring.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^users/', include('japper.users.urls')),
)
