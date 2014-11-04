# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0008_state_last_status_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='first_seen',
            field=models.DateTimeField(default=datetime.datetime(2014, 11, 4, 22, 41, 47, 883439, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
