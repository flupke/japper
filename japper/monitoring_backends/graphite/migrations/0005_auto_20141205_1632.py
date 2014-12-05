# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0004_auto_20141203_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='critical_operator',
            field=models.SmallIntegerField(default=4, choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='metric_aggregator',
            field=models.SmallIntegerField(default=0, help_text=b'The last 1 minute of values from target are aggregated using this function. The result is then compared to the threshold values below.', choices=[(0, b'average'), (1, b'max'), (2, b'min')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='target',
            field=models.CharField(help_text=b'The graphite path to evaluate, you may use functions here. It must ouptut a single metric.', max_length=4096),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='warning_operator',
            field=models.SmallIntegerField(default=4, choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')]),
            preserve_default=True,
        ),
    ]
