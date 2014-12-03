# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0003_check_metric_aggregator'),
    ]

    operations = [
        migrations.RenameField(
            model_name='check',
            old_name='metric',
            new_name='target',
        ),
    ]
