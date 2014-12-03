# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0002_auto_20141203_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='check',
            name='metric_aggregator',
            field=models.SmallIntegerField(default=0, choices=[(0, b'average'), (1, b'max'), (2, b'min')]),
            preserve_default=True,
        ),
    ]
