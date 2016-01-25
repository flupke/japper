# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphite', '0006_auto_20160125_1745'),
    ]

    operations = [
        migrations.RenameField(
            model_name='check',
            old_name='target',
            new_name='query',
        ),
    ]
