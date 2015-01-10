from django.db import models
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import get_template

from japper.monitoring.plugins.models import AlertSinkBase
from japper.utils import build_absolute_uri
from . import settings


class AlertSink(AlertSinkBase):

    def send_alert(self, prev_state, new_state, user=None, debug_timestamp=''):
        if user is None or not user.email.strip():
            return

        context = Context({
            'prev_state': prev_state,
            'new_state': new_state,
            'state_url': build_absolute_uri(new_state.get_absolute_url()),
            'debug_timestamp': debug_timestamp,
        })
        subject_template = get_template('django_email/subject.txt')
        subject = subject_template.render(context).strip()
        body_template = get_template('django_email/body.txt')
        body = body_template.render(context)
        send_mail(subject, body, settings.FROM_EMAIL, [user.email])

    @models.permalink
    def get_absolute_url(self):
        return 'django_email_update_alert_sink', [self.pk]
