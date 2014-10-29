# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0006_auto_20141028_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='state',
            name='last_checked',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
