# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_subscriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='subscriptions',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
