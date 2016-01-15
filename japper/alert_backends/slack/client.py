import json
from japper.utils import HttpClient


class SlackWebhookClient(HttpClient):

    def __init__(self, webhook_url, *args, **kwargs):
        super(SlackWebhookClient, self).__init__(*args, **kwargs)
        self.webhook_url = webhook_url

    def post_raw_message(self, message):
        self.post(self.webhook_url, data=json.dumps(message))

    def post_message(self, text, attachment_color=None, attachment_title=None,
                     attachment_text=None, icon_url=None, channel=None):
        message = {'text': text}
        if icon_url is not None:
            message['icon_url'] = icon_url
        if channel is not None:
            message['channel'] = channel
        attachment_field = {}
        if attachment_title is not None:
            attachment_field['title'] = attachment_title
        if attachment_text is not None:
            attachment_field['value'] = attachment_text
        if attachment_field:
            attachment_field['short'] = False
            attachment = {
                'fallback': text,
                'fields': [attachment_field],
            }
            if attachment_color is not None:
                attachment['color'] = attachment_color
            message['attachments'] = [attachment]
        self.post_raw_message(message)
