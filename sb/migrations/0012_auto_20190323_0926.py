# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0011_auto_20161013_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedoc',
            name='editedTime',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2019, 3, 23, 9, 26, 2, 715919, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='scenario',
            name='cctransactions',
            field=models.ManyToManyField(to='sb.CCTransaction', blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='transactions',
            field=models.ManyToManyField(to='sb.Transaction', blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='sourcedoc',
            name='recordedTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='transactionseries',
            name='name',
            field=models.CharField(unique=True, help_text='A good, descriptive name for the series', max_length=100),
        ),
        migrations.AlterField(
            model_name='transactionseries',
            name='scenarios',
            field=models.ManyToManyField(to='sb.Scenario', blank=True),
        ),
    ]
