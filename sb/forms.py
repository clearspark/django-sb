from decimal import Decimal
from django import forms
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory, BaseFormSet
#from autocomplete_light import modelform_factory
from sb import models

class PaySlipForm(forms.ModelForm):
    class Meta:
        model = models.Payslip
        exclude=['docType', 'employee']

class ReimbursementForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, required=False)
    account = forms.ModelChoiceField(models.Account.objects.all())

ReimbursementFormSet = formset_factory(ReimbursementForm, extra=3)

class InterestForm(forms.Form):
    docNumber = forms.CharField(max_length=40)
    date = forms.DateField()
    accounts = forms.ModelMultipleChoiceField(models.Account.objects.filter(parent__name="Creditors"))
    expense = forms.ModelChoiceField(models.Account.objects.filter(parent__name="Interest Cost"))
    year = forms.IntegerField(min_value=2010, max_value=2015)
    month = forms.IntegerField(min_value=1, max_value=12)
    rate = forms.DecimalField()
    compoundInterval = forms.ChoiceField(choices=(('monthly', 'Monthly'),))

class SourceDocForm(forms.ModelForm):
    class Meta:
        model = models.SourceDoc
        fields = '__all__'

class InvoiceForm(forms.ModelForm):
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
    client = forms.ModelChoiceField(models.Client.objects.all())
    isQuote = forms.BooleanField(initial=False, required=False)
    date = forms.DateField(required=True)
    comments = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': 90}),
            help_text="Goes in accounting app, client does not see this.")
    clientSummary = forms.CharField(max_length=200, required=True,
            widget = forms.Textarea(attrs={'cols': 90, 'rows': 2, 'maxlength': 200}),
            help_text="Summary for Client. HTML styling tags can be used.")
    department = forms.ModelChoiceField(models.Department.objects.all())
        

class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = models.InvoiceLine
        fields = ('description', 'amount', 'vat')
        widgets = {
            'description': forms.TextInput(attrs={'size':60})
        }

InvoiceLinesFormSet = modelformset_factory(models.InvoiceLine, form=InvoiceLineForm, extra=2)

class GetInvoiceForm(forms.Form):
    vendor = forms.ModelChoiceField(models.Account.objects.filter(parent__name="Creditors"))
    spentOn = forms.ModelChoiceField(models.Account.objects.filter(cat__in=["Expense", "Asset"]), label="Spent on")
    amount = forms.DecimalField(max_digits=16, decimal_places=2)
    date = forms.DateField()
    vat = forms.ChoiceField(choices=(('auto', 'Auto'), ('specify', 'Specify'), ('none', 'None')),
        help_text='Please specify whether VAT is to be added automatically, manually specified or left out.', required=True)
    VATAmount = forms.DecimalField(label="VAT amount", max_digits=16, decimal_places=2, required=False)
    comments = forms.CharField(required=False, widget=forms.Textarea())
    department = forms.ModelChoiceField(models.Department.objects.all())

class AccountFilter(forms.Form):
    debitAccount = forms.ModelMultipleChoiceField(queryset = models.Account.objects.all(), required=False)
    creditAccount = forms.ModelMultipleChoiceField(queryset = models.Account.objects.all(), required=False)

class ClientStatementForm(forms.Form):
    client = forms.ModelChoiceField(models.Client.objects.all(), label="Client")
    statementDate = forms.DateField(required=True)
    startDate = forms.DateField(help_text="Date from which to show transactions", required=True)

class CCContributionForm(forms.Form):
    costCentre = forms.ModelChoiceField(queryset=models.Account.objects.filter(cat__in=models.INTERNAL_SHEET_CATS), required=True)
    fraction = forms.DecimalField(max_digits=5, decimal_places=4, required=True)

class CCContributionFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        total = sum([f.cleaned_data.get('fraction', Decimal('0.0000')) for f in self.forms])
        if total > Decimal('1.0000'):
            raise forms.ValidationError("Fractions cannot exceed a total of 1")
        
CCCForms = formset_factory(form=CCContributionForm, formset=CCContributionFormSet, extra=3)

class NewExpenseClaimForm(forms.ModelForm):
    class Meta:
        model = models.ExpenseClaim 
        fields = ['department', 'claimComments', 'claimAmount']

class ExpenseClaimReviewForm(forms.ModelForm):
    class Meta:
        model = models.ExpenseClaim
        fields = ['reviewComments', 'approvedAmount']

class SupportingDocForm(forms.ModelForm):
    class Meta:
        model = models.SupportingDoc
        fields = ['description', 'document']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['date', 'amount', 'debitAccount', 'creditAccount', 'isConfirmed']

class CCTransactionForm(forms.ModelForm):
    class Meta:
        model = models.CCTransaction
        fields = ['date', 'amount', 'debitAccount', 'creditAccount', 'isConfirmed']

TransactionFormSet = modelformset_factory(models.Transaction, fields=['date', 'amount', 'debitAccount', 'creditAccount', 'isConfirmed'], extra=2)
CCTransactionFormSet = modelformset_factory(models.CCTransaction, fields=['date', 'amount', 'debitAccount', 'creditAccount', 'isConfirmed'], extra=2)
