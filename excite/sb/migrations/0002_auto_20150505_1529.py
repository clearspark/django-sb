# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('timeFraction', models.DecimalField(max_digits=4, decimal_places=4)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isActive', models.BooleanField(help_text=b'Is employee currently working?')),
                ('account', models.ForeignKey(to='sb.Account')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='description',
            field=models.TextField(default='TODO'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='department',
            field=models.ForeignKey(to='sb.Department'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='employee',
            field=models.ForeignKey(to='sb.Employee'),
        ),
    ]
