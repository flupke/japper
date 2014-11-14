# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='initial_bad_status_reported',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
