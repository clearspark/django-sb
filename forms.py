from django import forms
from django.forms.formsets import formset_factory
from csdjango.sb import models

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

class DateRangeFilter(forms.Form):
    begin = forms.DateField(required=False)
    end = forms.DateField(required=False)

    def get_range(self):
        if self.is_valid():
            return self.cleaned_data.get('begin', None), self.cleaned_data.get('end', None)
        else:
            return None, None
