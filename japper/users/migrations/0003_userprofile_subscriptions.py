# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20141030_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='subscriptions',
            field=models.TextField(default=b'', editable=False),
            preserve_default=True,
        ),
    ]
