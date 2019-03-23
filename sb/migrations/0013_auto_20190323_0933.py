# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def update_source_doc_dates(apps, schema_editor):
    SourceDoc = apps.get_model('sb', 'SourceDoc')
    for doc in SourceDoc.objects.all():
        if doc.transactions.exists():
            doc.editedTime = doc.transactions.aggregate(models.Max('recordedTime'))['recordedTime__max']
            doc.recordedTime = doc.transactions.aggregate(models.Min('recordedTime'))['recordedTime__min']
            doc.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sb', '0012_auto_20190323_0926'),
    ]

    operations = [
            migrations.RunPython(update_source_doc_dates),
    ]
