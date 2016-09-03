# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0003_auto_20150507_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='timeFraction',
            field=models.DecimalField(max_digits=5, decimal_places=4),
        ),
    ]
