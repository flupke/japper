# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0007_auto_20160125_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='query',
            field=models.TextField(help_text=b'The graphite path to evaluate, you may use functions here. It must ouptut a single metric.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='monitoringsource',
            name='dead_hosts_query',
            field=models.TextField(default=b'', help_text=b'A graphite query that targets dead servers, used to remove dead dynamic hosts from Japper.', blank=True),
            preserve_default=True,
        ),
    ]
