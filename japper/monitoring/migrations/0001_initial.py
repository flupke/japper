# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import japper.monitoring.plugins
import japper.monitoring.models
import jsonfield.fields
import enumfields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('source_id', models.PositiveIntegerField()),
                ('host', models.CharField(max_length=255, null=True)),
                ('status', enumfields.fields.EnumIntegerField(max_length=10, enum=japper.monitoring.plugins.CheckStatus)),
                ('metrics', jsonfield.fields.JSONField(null=True)),
                ('source_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255, null=True, db_index=True)),
                ('status', enumfields.fields.EnumIntegerField(db_index=True, max_length=10, enum=japper.monitoring.models.Status)),
                ('metrics', jsonfield.fields.JSONField(null=True)),
                ('last_checked', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('source_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('source_type', 'source_id', 'name')]),
        ),
        migrations.AlterIndexTogether(
            name='state',
            index_together=set([('source_type', 'source_id')]),
        ),
        migrations.AlterIndexTogether(
            name='checkresult',
            index_together=set([('source_type', 'source_id')]),
        ),
    ]
