# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0008_auto_20160903_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scenario',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, help_text='A good, descriptive name for the scenario')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionBlueprint',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=16)),
                ('adjustment', models.CharField(max_length=253, help_text='\n        {Y|M}{+|-|*}{amount}\n        Example:\n            Y*1.1\n            M+1000.0')),
                ('creditAccount', models.ForeignKey(related_name='credits+', to='sb.Account')),
                ('debitAccount', models.ForeignKey(related_name='debits+', to='sb.Account')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionSeries',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, help_text='A good, descriptive name for the series')),
                ('startDate', models.DateField(blank=True, help_text='Date of the first transaction in the series')),
                ('endDate', models.DateField(blank=True, help_text='Date after which the series will end.')),
                ('repeatFormula', models.CharField(max_length=253, help_text='\n            The formula is specified by a series of steps.\n            The steps are separated spaces.\n            Each step specifies a movement.\n            D = Day, M = Month, Y = Year, W = Week\n            wd = workday, ME = Month End\n\n            Y{+|-}{n}\n            M{+|-|=}{n}\n            W{+|-}{n}\n            D{+|-|=}{n|ME}\n            D{>|=>|<|<=}{wd|ME}\n\n            Example:\n            Every year on same day: Y+1\n            Every month: M+1\n            Every week: W+1\n            3 days before month end: M+1 D=ME D-3\n            first Wednesday every month: M+1 D=1 D=>Wednesday\n            ')),
                ('comment', models.TextField(blank=True)),
                ('scenarios', models.ManyToManyField(to='sb.Scenario')),
            ],
        ),
        migrations.DeleteModel(
            name='CostCentre',
        ),
        migrations.AlterField(
            model_name='cctransaction',
            name='isConfirmed',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='invoiceSuffix',
            field=models.CharField(max_length=12, unique=True),
        ),
        migrations.AlterField(
            model_name='department',
            name='costCentre',
            field=models.ForeignKey(to='sb.Account'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='isConfirmed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='transactionblueprint',
            name='series',
            field=models.ForeignKey(related_name='transaction_blueprints', to='sb.TransactionSeries'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='cctransactions',
            field=models.ManyToManyField(to='sb.CCTransaction', blank=True),
        ),
        migrations.AddField(
            model_name='scenario',
            name='transactions',
            field=models.ManyToManyField(to='sb.Transaction', blank=True),
        ),
        migrations.AddField(
            model_name='cctransaction',
            name='series',
            field=models.ForeignKey(blank=True, null=True, to='sb.TransactionSeries'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='series',
            field=models.ForeignKey(blank=True, null=True, to='sb.TransactionSeries'),
        ),
    ]
