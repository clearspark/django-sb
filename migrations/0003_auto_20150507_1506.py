# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0002_auto_20150505_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payslip',
            fields=[
                ('sourcedoc_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sb.SourceDoc')),
                ('date', models.DateField()),
                ('gross', models.DecimalField(max_digits=16, decimal_places=2)),
                ('uif', models.DecimalField(max_digits=16, decimal_places=2)),
                ('paye', models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)),
            ],
            bases=('sb.sourcedoc',),
        ),
        migrations.AddField(
            model_name='employee',
            name='initials',
            field=models.CharField(default='TODO', max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payslip',
            name='employee',
            field=models.ForeignKey(to='sb.Employee'),
        ),
    ]
