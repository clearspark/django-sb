# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sb.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('sb', '0005_auto_20150507_1740'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseClaim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('claimAmount', models.DecimalField(max_digits=16, decimal_places=2)),
                ('claimComments', models.TextField(blank=True)),
                ('submitted', models.BooleanField(default=False)),
                ('reviewDate', models.DateTimeField(null=True, editable=False, blank=True)),
                ('reviewComments', models.TextField(blank=True)),
                ('approvedAmount', models.DecimalField(null=True, max_digits=16, decimal_places=2, blank=True)),
                ('claimant', models.ForeignKey(related_name='expenseClaimsMade', to='sb.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='SupportingDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('description', models.CharField(help_text=b'Brief description of document, what it is and what it says.\n                         Example: "Invoice showing expense incurred"', max_length=250)),
                ('document', models.FileField(upload_to=sb.models.supporting_doc_file_path, verbose_name=b'File')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AddField(
            model_name='department',
            name='expenseReviewers',
            field=models.ManyToManyField(to='sb.Employee'),
        ),
        migrations.AddField(
            model_name='expenseclaim',
            name='department',
            field=models.ForeignKey(to='sb.Department'),
        ),
        migrations.AddField(
            model_name='expenseclaim',
            name='reviewedBy',
            field=models.ForeignKey(related_name='expenseClaimsReviewd', blank=True, to='sb.Employee', null=True),
        ),
    ]
