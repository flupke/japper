# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0008_auto_20160125_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoringsource',
            name='aggregate_over',
            field=models.IntegerField(default=60, help_text=b'Aggregate metrics over this number of seconds'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='query',
            field=models.TextField(help_text=b'The graphite query to evaluate, you may use functions here. It may output multiple metrics.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='monitoringsource',
            name='dead_hosts_query',
            field=models.TextField(default=b'', help_text=b'A graphite search query that targets dead servers hostnames, used to remove dead dynamic hosts from Japper. For example if dead servers metrics are stored in "dead-servers.[hostname].cpu.idle", the query to target the hostname would be "dead-servers.*".', blank=True),
            preserve_default=True,
        ),
    ]
