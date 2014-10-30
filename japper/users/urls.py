from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import UpdateUserProfile


urlpatterns = patterns('',
    url(r'^profile/$',
        login_required(UpdateUserProfile.as_view()),
        name='users_profile'),
)
