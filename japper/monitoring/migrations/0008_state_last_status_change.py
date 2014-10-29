# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0007_auto_20141029_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='last_status_change',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
