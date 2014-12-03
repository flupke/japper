# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0001_squashed_0003_auto_20141203_1550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='critical_operator',
            field=models.SmallIntegerField(choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='warning_operator',
            field=models.SmallIntegerField(choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')]),
            preserve_default=True,
        ),
    ]
