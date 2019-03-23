# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0013_auto_20190323_0933'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CostCentre',
        ),
    ]
