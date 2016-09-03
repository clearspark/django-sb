# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sb.models


class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0007_invoice_isquote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='cat',
            field=models.CharField(max_length=200, choices=[('equity', 'Equity'), ('asset', 'Asset'), ('liability', 'Liability'), ('income', 'Income'), ('expense', 'Expense'), ('cost_centre', 'Cost centre')]),
        ),
        migrations.AlterField(
            model_name='asset',
            name='category',
            field=models.CharField(max_length=50, choices=[('land', 'Land'), ('equipment', 'Equipment')], verbose_name='Asset category'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to=sb.models.asset_image_file_path, verbose_name='Optional: photo of asset'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='residualValue',
            field=models.DecimalField(max_digits=16, decimal_places=2, help_text='Estimated resale value of asset in current condition on current date.'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='usefulLife',
            field=models.IntegerField(verbose_name='Usefull lifespan in months'),
        ),
        migrations.AlterField(
            model_name='client',
            name='address',
            field=models.TextField(help_text='This will be used for generating invoices and statements. HTML tags can be used. Should include Company name, registration, VAT nr etc.'),
        ),
        migrations.AlterField(
            model_name='client',
            name='invoiceOffset',
            field=models.IntegerField(default=0, help_text='The invoice number will be increaced by this number.\n    The reason this is needed is that not all invoices in the database are explicitly represented as such and this '),
        ),
        migrations.AlterField(
            model_name='client',
            name='invoiceTemplate',
            field=models.TextField(blank=True, default='{% include "sb/default_invoice_template.html" %}'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='isActive',
            field=models.BooleanField(help_text='Is employee currently working?'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='clientSummary',
            field=models.CharField(max_length=200, help_text='One or two sentence description of what invoice is for.  Will shown on invoice above line items. Possibly on statements.'),
        ),
        migrations.AlterField(
            model_name='sourcedoc',
            name='comments',
            field=models.TextField(blank=True, help_text='Any comments/extra info/meta data about this doc.'),
        ),
        migrations.AlterField(
            model_name='sourcedoc',
            name='docType',
            field=models.CharField(max_length=20, help_text='The type of document being recorded/created', choices=[('bank-statement', 'Bank statement'), ('invoice-out', 'Outbound invoice'), ('invoice-in', 'Inbound invoice'), ('payslip', 'Payslip'), ('other', 'Other')]),
        ),
        migrations.AlterField(
            model_name='sourcedoc',
            name='electronicCopy',
            field=models.FileField(blank=True, null=True, upload_to=sb.models.source_doc_file_path, verbose_name='Electronic copy'),
        ),
        migrations.AlterField(
            model_name='sourcedoc',
            name='number',
            field=models.CharField(max_length=40, unique=True, help_text='Document number'),
        ),
        migrations.AlterField(
            model_name='supportingdoc',
            name='description',
            field=models.CharField(max_length=250, help_text='Brief description of document, what it is and what it says.\n                         Example: "Invoice showing expense incurred"'),
        ),
        migrations.AlterField(
            model_name='supportingdoc',
            name='document',
            field=models.FileField(upload_to=sb.models.supporting_doc_file_path, verbose_name='File'),
        ),
    ]
