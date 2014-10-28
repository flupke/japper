# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_checkresult_output'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='state',
            unique_together=set([('source_type', 'source_id', 'host', 'name')]),
        ),
        migrations.AlterIndexTogether(
            name='state',
            index_together=set([]),
        ),
    ]
