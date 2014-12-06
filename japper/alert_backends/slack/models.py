from django.db import models
from django.utils.functional import cached_property
from django.contrib.staticfiles.storage import staticfiles_storage

from japper.monitoring.plugins.models import AlertSinkBase
from japper.monitoring.status import Status
from japper.monitoring.search import build_search_url
from japper.utils import build_absolute_uri
from .client import SlackWebhookClient


class AlertSink(AlertSinkBase):

    webhook_url = models.CharField(max_length=4096)
    channel = models.CharField(max_length=255, null=True, blank=True)

    def send_alert(self, prev_state, new_state, user=None):
        # Send to global channel or user
        if (user is not None
                and user.profile.slack_nickname is not None
                and user.profile.slack_nickname.strip()):
            channel = '@%s' % user.profile.slack_nickname
        elif self.channel is not None and self.channel.strip():
            channel = '#%s' % self.channel
        else:
            channel = None

        icon_url = build_absolute_uri(
                staticfiles_storage.url('img/Puppy-Bones.png'))

        if new_state.status == Status.passing:
            color = '#36A64F'
        elif new_state.status == Status.warning:
            color = '#DAA038'
        elif new_state.status == Status.critical:
            color = '#D00000'
        else:
            color = None

        if new_state.status.is_problem():
            text_prefix = '*PROBLEM*'
        else:
            text_prefix = '*RECOVERY*'
        state_link = format_slack_link(
                build_absolute_uri(new_state.get_absolute_url()),
                new_state.full_path())
        text = '%s - %s is *%s*' % (text_prefix, state_link,
                new_state.status.name.upper())

        if prev_state:
            attachment_title = 'State changed from %s to %s' % (
                    prev_state.status.name.upper(),
                    new_state.status.name.upper())
        else:
            attachment_title = None

        source = format_slack_link(
                build_absolute_uri(build_search_url(source=new_state.source)),
                new_state.source)
        if new_state.host:
            host = format_slack_link(
                    build_absolute_uri(build_search_url(host=new_state.host)),
                    new_state.host)
        else:
            host = ''
        name = format_slack_link(
                build_absolute_uri(build_search_url(name=new_state.name)),
                new_state.name)

        if new_state.output:
            attachment_text = 'Output: %s' % new_state.output
        else:
            attachment_text = ''
        attachment_text += '''
Source: {source}
Host: {host}
Name: {name}'''.format(source=source, host=host, name=name)

        self.client.post_message(text, channel=channel, icon_url=icon_url,
                attachment_color=color, attachment_title=attachment_title,
                attachment_text=attachment_text)

    @cached_property
    def client(self):
        # Cached so keepalive connections can be used
        return SlackWebhookClient(self.webhook_url)

    @models.permalink
    def get_absolute_url(self):
        return 'slack_update_alert_sink', [self.pk]


def format_slack_link(url, label=None):
    if label:
        return '<%s|%s>' % (url, label)
    else:
        return '<%s>' % url
