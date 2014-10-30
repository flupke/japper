from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField


class UserProfile(models.Model):
    '''
    Extended user infos.
    '''

    user = AutoOneToOneField(User, related_name='profile')
    mobile = models.CharField(max_length=255, blank=True)
    subscriptions = models.TextField(default='')

