# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0009_auto_20160129_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='check',
            name='matrix_metrics',
            field=models.BooleanField(default=False, help_text=b'If checked, expect a matrix result from the graphite query. This means that the metrics returned are indexed by hostname and some other axis. For example if you have disk metrics indexed by hostname and mount point, e.g. "servers.[hostname].disk.[mount_point].free_percent", metrics should be aliased as "[hostname].[mount_point]" (using the "aliasSub()" graphite function).'),
            preserve_default=True,
        ),
    ]
