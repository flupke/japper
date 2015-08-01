# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_auto_20141211_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='muted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
