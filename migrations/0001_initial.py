# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import sb.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('cat', models.CharField(max_length=200, choices=[(b'equity', b'Equity'), (b'asset', b'Asset'), (b'liability', b'Liability'), (b'income', b'Income'), (b'expense', b'Expense'), (b'cost_centre', b'Cost centre')])),
                ('gl_code', models.CharField(max_length=20, blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='sb.Account', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(unique=True, max_length=20)),
                ('description', models.TextField()),
                ('location', models.TextField()),
                ('image', models.FileField(upload_to=sb.models.asset_image_file_path, null=True, verbose_name=b'Optional: photo of asset', blank=True)),
                ('cost', models.DecimalField(max_digits=16, decimal_places=2)),
                ('accDepreciation', models.DecimalField(max_digits=16, decimal_places=2)),
                ('carryingValue', models.DecimalField(max_digits=16, decimal_places=2)),
                ('usefulLife', models.IntegerField(verbose_name=b'Usefull lifespan in months')),
                ('category', models.CharField(max_length=50, verbose_name=b'Asset category', choices=[(b'land', b'Land'), (b'equipment', b'Equipment')])),
                ('residualValue', models.DecimalField(help_text=b'Estimated resale value of asset in current condition on current date.', max_digits=16, decimal_places=2)),
                ('disposalDate', models.DateField(null=True, blank=True)),
                ('disposalValue', models.DecimalField(max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Bookie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('canSendInvoice', models.BooleanField(default=False)),
                ('canReceiveInvoice', models.BooleanField(default=False)),
                ('canAddPayslip', models.BooleanField(default=False)),
                ('canApplyInterest', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='bookie', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CCTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=16, decimal_places=2)),
                ('date', models.DateField()),
                ('recordedTime', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(blank=True)),
                ('isConfirmed', models.BooleanField()),
                ('creditAccount', models.ForeignKey(related_name='cc_credits', to='sb.Account')),
                ('debitAccount', models.ForeignKey(related_name='cc_debits', to='sb.Account')),
                ('recordedBy', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', 'pk'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('displayName', models.CharField(max_length=100)),
                ('invoiceTemplate', models.TextField(default=b'{% include "sb/default_invoice_template.html" %}', blank=True)),
                ('statementTemplate', models.TextField(blank=True)),
                ('invoiceSuffix', models.CharField(max_length=12)),
                ('invoiceOffset', models.IntegerField(default=0, help_text=b'The invoice number will be increaced by this number.\n    The reason this is needed is that not all invoices in the database are explicitly represented as such and this ')),
                ('address', models.TextField(help_text=b'This will be used for generating invoices and statements. HTML tags can be used. Should include Company name, registration, VAT nr etc.')),
                ('account', models.ForeignKey(to='sb.Account')),
                ('adminGoup', models.ForeignKey(to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('longName', models.CharField(max_length=255)),
                ('shortName', models.CharField(max_length=8)),
                ('minMonthlyDeduction', models.DecimalField(max_digits=16, decimal_places=2)),
                ('invoiceDeductionFraction', models.DecimalField(max_digits=4, decimal_places=4)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1000)),
                ('amount', models.DecimalField(max_digits=16, decimal_places=2)),
                ('vat', models.DecimalField(max_digits=16, decimal_places=2)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='SourceDoc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(help_text=b'Document number', unique=True, max_length=40)),
                ('electronicCopy', models.FileField(upload_to=sb.models.source_doc_file_path, null=True, verbose_name=b'Electronic copy', blank=True)),
                ('recordedTime', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(help_text=b'Any comments/extra info/meta data about this doc.', blank=True)),
                ('docType', models.CharField(help_text=b'The type of document being recorded/created', max_length=20, choices=[(b'bank-statement', b'Bank statement'), (b'invoice-out', b'Outbound invoice'), (b'invoice-in', b'Inbound invoice'), (b'payslip', b'Payslip'), (b'other', b'Other')])),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=16, decimal_places=2)),
                ('date', models.DateField()),
                ('recordedTime', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(blank=True)),
                ('isConfirmed', models.BooleanField()),
                ('creditAccount', models.ForeignKey(related_name='credits', to='sb.Account')),
                ('debitAccount', models.ForeignKey(related_name='debits', to='sb.Account')),
                ('recordedBy', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date', 'pk'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('sourcedoc_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sb.SourceDoc')),
                ('html', models.TextField(blank=True)),
                ('invoiceDate', models.DateField()),
                ('finalized', models.BooleanField(default=False)),
                ('clientSummary', models.CharField(help_text=b'One or two sentence description of what invoice is for.  Will shown on invoice above line items. Possibly on statements.', max_length=200)),
                ('client', models.ForeignKey(to='sb.Client')),
            ],
            bases=('sb.sourcedoc',),
        ),
        migrations.AddField(
            model_name='transaction',
            name='sourceDocument',
            field=models.ForeignKey(related_name='transactions', blank=True, to='sb.SourceDoc', null=True),
        ),
        migrations.AddField(
            model_name='sourcedoc',
            name='recordedBy',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cctransaction',
            name='sourceDocument',
            field=models.ForeignKey(related_name='cc_transactions', blank=True, to='sb.SourceDoc', null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='acquisitionTransaction',
            field=models.ForeignKey(to='sb.Transaction'),
        ),
        migrations.CreateModel(
            name='CostCentre',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('sb.account',),
        ),
        migrations.AddField(
            model_name='invoiceline',
            name='invoice',
            field=models.ForeignKey(to='sb.Invoice'),
        ),
        migrations.AddField(
            model_name='department',
            name='costCentre',
            field=models.ForeignKey(to='sb.CostCentre'),
        ),
    ]
