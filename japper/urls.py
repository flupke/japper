from django.conf.urls import include, url
from django.contrib import admin

from japper.monitoring.plugins import get_url_patterns


urlpatterns = get_url_patterns('',
    # Examples:
    # url(r'^$', 'japper.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^monitoring/', include('japper.monitoring.urls')),
)
