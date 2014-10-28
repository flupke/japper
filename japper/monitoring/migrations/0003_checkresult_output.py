# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_checkresult_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkresult',
            name='output',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
    ]
