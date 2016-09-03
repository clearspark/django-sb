# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0006_auto_20150508_2209'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='isQuote',
            field=models.BooleanField(default=False),
        ),
    ]
