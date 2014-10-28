# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0004_auto_20141028_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='output',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
    ]
