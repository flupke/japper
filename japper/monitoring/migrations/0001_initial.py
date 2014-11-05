# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import japper.monitoring.status
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
                ('source_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=255)),
                ('host', models.CharField(max_length=255, null=True)),
                ('status', enumfields.fields.EnumIntegerField(max_length=10, enum=japper.monitoring.status.Status)),
                ('output', models.CharField(max_length=255, null=True)),
                ('metrics', jsonfield.fields.JSONField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
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
                ('name', models.CharField(max_length=255, db_index=True)),
                ('host', models.CharField(max_length=255, null=True, db_index=True)),
                ('status', enumfields.fields.EnumIntegerField(db_index=True, max_length=10, enum=japper.monitoring.status.Status)),
                ('output', models.CharField(max_length=255, null=True)),
                ('metrics', jsonfield.fields.JSONField(null=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_checked', models.DateTimeField()),
                ('last_status_change', models.DateTimeField(null=True)),
                ('source_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('source_type', 'source_id', 'host', 'name')]),
        ),
        migrations.AddField(
            model_name='checkresult',
            name='state',
            field=models.ForeignKey(related_name='check_results', to='monitoring.State'),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='checkresult',
            index_together=set([('source_type', 'source_id')]),
        ),
    ]
