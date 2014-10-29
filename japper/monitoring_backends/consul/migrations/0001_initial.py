# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoringSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('endpoints', models.TextField(help_text=b'List of consul HTTP endpoints, e.g. http://localhost:8500/')),
                ('dynamic_hosts', models.BooleanField(default=False, help_text=b'Use this option when the list of hosts in this group is dynamic (e.g. when using autoscaling on EC2) and offline hosts should be removed instead of generating alerts')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
