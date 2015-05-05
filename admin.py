from django.contrib import admin
from autocomplete_light import modelform_factory
from sb import models

class TransactionInline(admin.StackedInline):
    model = models.Transaction
    form = modelform_factory(models.Transaction, fields='__all__')
    extra = 2

class CCTransactionInline(admin.StackedInline):
    model = models.CCTransaction
    form = modelform_factory(models.CCTransaction, fields='__all__')
    extra = 2

class InvoiceLineInline(admin.StackedInline):
    model = models.InvoiceLine
    extra = 2

class TransactionAdmin(admin.ModelAdmin):
    form = modelform_factory(models.Transaction, fields='__all__')
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
    inlines = [TransactionInline, CCTransactionInline]
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
    list_display = ["long_name", "name", "cat", "balance", "dt_count", "ct_count", 'gl_code']
    list_filter = ["parent", "cat"]

class CCAdmin(AccountAdmin):
    list_filter = ["parent"]
    def queryset(self, request):
        qs = super(CCAdmin, self).queryset(request)
        return qs.filter(cat__in=models.INTERNAL_SHEET_CATS)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'client']
    list_filter = ['client']
    inlines = [InvoiceLineInline, TransactionInline]

class AppointmentInline(admin.TabularInline):
    model = models.Appointment
    extra = 1

class EmployeeAdmin(admin.ModelAdmin):
    inlines = [AppointmentInline]
    list_filter = ['appointment__department']

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.CostCentre, CCAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.CCTransaction, TransactionAdmin)
admin.site.register(models.SourceDoc, SourceDocAdmin)
admin.site.register(models.Asset)
admin.site.register(models.Bookie)
admin.site.register(models.Client)
admin.site.register(models.Employee, EmployeeAdmin)
admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.InvoiceLine)
admin.site.register(models.Department)
