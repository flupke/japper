# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'graphite', '0001_initial'), (b'graphite', '0002_auto_20141203_1057'), (b'graphite', '0003_auto_20141203_1550')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonitoringSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('endpoint', models.CharField(help_text=b'The URL of the graphite, endpoint', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Check',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('metric', models.CharField(max_length=4096)),
                ('host', models.CharField(max_length=255, null=True, blank=True)),
                ('warning_operator', models.IntegerField(choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')])),
                ('warning_value', models.FloatField()),
                ('critical_operator', models.IntegerField(choices=[(0, b'<'), (1, b'<='), (2, b'=='), (3, b'!='), (4, b'>='), (5, b'>')])),
                ('critical_value', models.FloatField()),
                ('source', models.ForeignKey(related_name='checks', editable=False, to='graphite.MonitoringSource')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='monitoringsource',
            name='endpoint',
            field=models.CharField(help_text=b'The base URL of the graphite endpoint', max_length=4096),
            preserve_default=True,
        ),
    ]
