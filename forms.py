from django import forms
from django.forms.formsets import formset_factory
from sb import models

class PaySlipForm(forms.Form):
    employee = forms.ModelChoiceField(models.Account.objects.filter(parent__name="Creditors"))
    date = forms.DateField()
    gross = forms.DecimalField(decimal_places=2)
    paye = forms.DecimalField(decimal_places=2, required=False)
    uif = forms.DecimalField(decimal_places=2, required=False)
    bonus = forms.DecimalField(decimal_places=2, required=False)

class ReimbursementForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, required=False)
    account = forms.ModelChoiceField(models.Account.objects.all())

ReimbursementFormSet = formset_factory(ReimbursementForm, extra=1)

class SourceDocForm(forms.ModelForm):
    class Meta:
        model = models.SourceDoc
        exclude = ['docType']

class DateRangeFilter(forms.Form):
    begin = forms.DateField(required=False)
    end = forms.DateField(required=False)

    def get_range(self):
        if self.is_valid():
            return self.cleaned_data.get('begin', None), self.cleaned_data.get('end', None)
        else:
            return None, None

class SendInvoiceForm(forms.Form):
    client = forms.ModelChoiceField(models.Account.objects.filter(parent__name="Debtors"))
    amount = forms.DecimalField(max_digits=16, decimal_places=2)
    date = forms.DateField()
    vat = forms.BooleanField(help_text='Add VAT?', required=False)
    comments = forms.CharField(required=False, widget=forms.Textarea())

class GetInvoiceForm(forms.Form):
    vendor = forms.ModelChoiceField(models.Account.objects.filter(parent__name="Creditors"))
    spentOn = forms.ModelChoiceField(models.Account.objects.filter(cat__in=["Expense", "Asset"]), label="Spent on")
    amount = forms.DecimalField(max_digits=16, decimal_places=2)
    date = forms.DateField()
    vat = forms.ChoiceField(choices=(('auto', 'Auto'), ('specify', 'Specify'), ('none', 'None')),
        help_text='Please specify whether VAT is to be added automatically, manually specified or left out.', required=True)
    VATAmount = forms.DecimalField(label="VAT amount", max_digits=16, decimal_places=2, required=False)
    comments = forms.CharField(required=False, widget=forms.Textarea())

class AccountFilter(forms.Form):
    debitAccount = forms.ModelChoiceField(queryset = models.Account.objects.all())
    creditAccount = forms.ModelChoiceField(queryset = models.Account.objects.all())
