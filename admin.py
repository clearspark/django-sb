from django.contrib import admin
from csdjango.sb import models

class TransactionsInline(admin.StackedInline):
    model = models.Transaction
    extra = 2

class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "debitAccount", "creditAccount", "amount", "comments"]
    list_filter = ["date",  "debitAccount", "creditAccount"]
    save_on_top = True
    def save_model(self, request, obj, form, change):
        #set_generic(request, obj, form, change)
        obj.recordedBy = request.user
        obj.save()

class SourceDocAdmin(admin.ModelAdmin):
    list_display = ["number"]
    inlines = [TransactionsInline]
    save_on_top = True
    def save_model(self, request, obj, form, change):
        #set_generic(request, obj, form, change)
        obj.recordedBy = request.user
        obj.save()

class AccountAdmin(admin.ModelAdmin):
    list_display = ["name", "balance"]

admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.SourceDoc, SourceDocAdmin)
