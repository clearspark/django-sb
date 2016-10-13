# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0009_auto_20160929_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionseries',
            name='cctransactions',
            field=models.ManyToManyField(blank=True, editable=False, to='sb.CCTransaction'),
        ),
        migrations.AddField(
            model_name='transactionseries',
            name='transactions',
            field=models.ManyToManyField(blank=True, editable=False, to='sb.Transaction'),
        ),
    ]
