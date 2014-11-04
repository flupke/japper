from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CreateAlertSink, UpdateAlertSink, DeleteAlertSink


urlpatterns = patterns('',
    url(r'^alert-sink/create/$',
        login_required(CreateAlertSink.as_view()),
        name='django_email_create_alert_sink'),
    url(r'^alert-sink/(?P<pk>\d+)/$',
        login_required(UpdateAlertSink.as_view()),
        name='django_email_update_alert_sink'),
    url(r'^alert-sink/(?P<pk>\d+)/delete/$',
        login_required(DeleteAlertSink.as_view()),
        name='django_email_delete_alert_sink'),
)
