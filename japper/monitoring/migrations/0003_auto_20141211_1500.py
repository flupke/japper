# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_state_initial_bad_status_reported'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkresult',
            name='output',
            field=models.CharField(max_length=4095, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='state',
            name='output',
            field=models.CharField(max_length=4095, null=True),
            preserve_default=True,
        ),
    ]
