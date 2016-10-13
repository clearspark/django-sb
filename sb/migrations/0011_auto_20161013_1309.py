# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0010_auto_20161013_1122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cctransaction',
            name='series',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='series',
        ),
        migrations.AddField(
            model_name='transactionblueprint',
            name='transactionType',
            field=models.CharField(default='normal', choices=[('normal', 'Normal'), ('costCentre', 'Cost centre')], max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transactionblueprint',
            name='adjustment',
            field=models.CharField(help_text='\n           Currently unavailable, leave blank\n           ', blank=True, max_length=253),
        ),
        migrations.AlterField(
            model_name='transactionseries',
            name='repeatFormula',
            field=models.CharField(help_text='<br/>The formula is specified by a series of steps.<br/>The steps are separated by spaces.<br/>Each step specifies a change in the date.<br/>D = Day, M = Month, Y = Year, W = Week<br/>wd = workday, ME = Month End<br/><br/>Y{+|-}{n}<br/>M{+|-|=}{n}<br/>W{+|-}{n}<br/>D{+|-|=}{n|ME}<br/>D{>|=>|<|<=}{wd|ME}<br/><br/>Example:<br/>Every year on same day: Y+1<br/>Every month: M+1<br/>Every week: W+1<br/>3 days before month end: M+1 D=ME D-3<br/>first Wednesday every month: M+1 D=1 D=>Wednesday<br/>', max_length=253),
        ),
    ]
