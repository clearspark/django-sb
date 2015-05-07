# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0004_auto_20150507_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payslip',
            name='paye',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='payslip',
            name='uif',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=16, decimal_places=2),
        ),
    ]
