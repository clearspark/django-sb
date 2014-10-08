from django.contrib import admin
from sb import models

class TransactionInline(admin.StackedInline):
    model = models.Transaction
    extra = 2

class InvoiceLineInline(admin.StackedInline):
    model = models.InvoiceLine
    extra = 2

class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "isConfirmed", "debitAccount", "creditAccount", "amount", "sourceDocument", "comments"]
    list_filter = ["date",  "debitAccount", "creditAccount"]
    save_on_top = True
    def save_model(self, request, obj, form, change):
        #set_generic(request, obj, form, change)
        obj.recordedBy = request.user
        obj.save()

class SourceDocAdmin(admin.ModelAdmin):
    list_display = ["number", "transaction_count", "has_file", 'docType']
    list_editable = ['docType']
    list_filter = ['docType', 'transactions__debitAccount', 'transactions__creditAccount']
    inlines = [TransactionInline]
    save_on_top = True
    def save_model(self, request, obj, form, change):
        #set_generic(request, obj, form, change)
        obj.recordedBy = request.user
        obj.save()
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.recordedBy = request.user
            instance.save()
        formset.save_m2m()

class AccountAdmin(admin.ModelAdmin):
    list_display = ["long_name", "name", "cat", "balance", "dt_count", "ct_count"]
    list_filter = ["parent", "cat"]

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'client']
    list_filter = ['client']
    inlines = [InvoiceLineInline, TransactionInline]

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.SourceDoc, SourceDocAdmin)
admin.site.register(models.Asset)
admin.site.register(models.Bookie)
admin.site.register(models.Client)
admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.InvoiceLine)
