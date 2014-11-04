from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from annoying.fields import AutoOneToOneField


class UserProfile(models.Model):
    '''
    Extended user infos.
    '''

    user = AutoOneToOneField(User, related_name='profile')
    mobile = models.CharField(max_length=255, blank=True)
    subscriptions = models.TextField(default='')


@receiver(models.signals.pre_delete)
def cleanup_subscriptions(sender, instance, using, **kwargs):
    # Since we use a dirty hack to store relationships between user profiles
    # and alert sinks, we need to add a custom cleanup hook too
    if hasattr(instance, 'get_alert_sink_text_link'):
        # Must be an AlertSink! remove its link from all subscriptions
        link = instance.get_alert_sink_text_link()
        for profile in UserProfile.objects.all():
            profile.subscriptions = profile.subscriptions.replace(link, '')
            profile.save()
