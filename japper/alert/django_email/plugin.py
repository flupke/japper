from django.core.mail import send_mail
from django.template import Template, Context
from django.template.loader import get_template

from japper.monitoring.plugins.alert_backend import AlertBackend
from japper.monitoring.models import StateStatus
from . import settings


class DjangoEmailBackend(AlertBackend):
    '''
    Send mails with Django SMTP wrapper.
    '''

    def send_alert(self, user, prev_state, new_state):
        context = Context({
            'prev_state': new_state,
            'new_state': new_state,
        })
        subject_template = get_template('alert/django_email/subject.txt')
        subject = subject_template.render(context)
        body_template = get_template('alert/django_email/body.txt')
        body = body_template.render(context)

        send_mail(subject, body, settings.FROM_EMAIL, [user.email])


def create_backend():
    return DjangoEmailBackend()
