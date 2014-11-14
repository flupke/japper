# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consul', '0001_initial'),
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
            name='search_ec2_public_dns',
            field=models.BooleanField(default=False, help_text=b'Use EC2 API to retrieve the public DNS of the hosts from their default hostname'),
            preserve_default=True,
        ),
    ]
