# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0005_auto_20141205_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoringsource',
            name='aws_access_key_id',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitoringsource',
            name='aws_region',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitoringsource',
            name='aws_secret_access_key',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitoringsource',
            name='dead_hosts_query',
            field=models.TextField(default=b'', help_text=b'A graphite query that targets dead servers, used to remove dead dynamic hosts from Japper.', max_length=4096, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitoringsource',
            name='dynamic_hosts',
            field=models.BooleanField(default=False, help_text=b'Use this option when the list of hosts from this source is dynamic (e.g. when using autoscaling on EC2) and offline hosts should be removed instead of generating alerts'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='monitoringsource',
            name='search_ec2_public_dns',
            field=models.BooleanField(default=False, help_text=b'Use EC2 API to retrieve the public DNS of the hosts from their default hostname'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='host',
            field=models.CharField(help_text=b'Host name to associate with this check. If left blank, use the target name(s) in the graphite query result', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='check',
            name='metric_aggregator',
            field=models.SmallIntegerField(default=0, help_text=b'The last 1 minute of values are aggregated using this function. The result is then compared to the threshold values below.', choices=[(0, b'average'), (1, b'max'), (2, b'min')]),
            preserve_default=True,
        ),
    ]
