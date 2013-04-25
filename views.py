from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from csdjango.sb import models, forms
# Create your views here.

def account_list(request):
    accounts = models.Account.objects.all()
    return render(request, "sb/account_list.html", {"accounts": accounts})

def account_details(request, pk):
    account = get_object_or_404(models.Account, pk=pk)
    #transactions = account.transactions()
    #class AccountMonth(object):
    #    def __init__(self, nr):
    #        self.nr = nr
    #        self.transactions = []
    #        self.dt_total = 0.0
    #        self.ct_total = 0.0
    #months = []
    #month = 0
    #for t in transactions:
    #    if t.date.month != month:
    #        curMonth = AccountMonth(t.date.month)
    #        months.append(curMonth)
    #    curMonth.transactions.append(t)
    #    if t.debitAccount = 


    return render(request, "sb/account_detail.html", {"account": account})

def doc_list(request):
    docs = models.SourceDoc.objects.all()
    return render(request, "sb/doc_list.html", {"docs": docs})

def doc_details(request, pk):
    doc = get_object_or_404(models.SourceDoc, pk=pk)
    return render(request, "sb/doc_detail.html", {"doc": doc})

def trans_details(request, pk):
    trans = get_object_or_404(models.Transaction, pk=pk)
    return render(request, "sb/trans_detail.html", {"trans": trans})

def trial_balance(request):
    accountDict = {
            "equity_accounts": models.Account.objects.filter(cat="equity").all(),
            "asset_accounts":  models.Account.objects.filter(cat="asset").all(),
            "liability_accounts": models.Account.objects.filter(cat="liability").all(),
            "income_accounts": models.Account.objects.filter(cat="income").all(),
            "expense_accounts": models.Account.objects.filter(cat="expense").all()}
    return render(request, "sb/trial_balance.html", accountDict)

def add_payslip(request):
    if request.method == "GET":
        pform = forms.PaySlipForm()
        dform = forms.SourceDocForm()
    elif request.method == "POST":
        pform = forms.PaySlipForm(request.POST)
        dform = forms.SourceDocForm(request.POST, request.FILES)
        if pform.is_valid() and dform.is_valid():
            #Read data
            sourceDoc = dform.save(commit=False)
            sourceDoc.recordedBy=request.user
            sourceDoc.save()
            pdata = pform.cleaned_data
            employee = pdata["employee"]
            date = pdata["date"]
            grossAmount = pdata["gross"]
            payeAmount = pdata["paye"]
            uifAmount = pdata.get("uif", None)
            bonusAmount = pdata.get("bonus", None)
            print(bonusAmount)

            salaries = models.Account.objects.get(name="Salaries")
            paye = models.Account.objects.get(name="PAYE")
            uif = models.Account.objects.get(name="UIF")
            sars = models.Account.objects.get(name="SARS")
            bonusses = models.Account.objects.get(name="Bonusses")
            #generate transactions
            if payeAmount > 0.00:
                #Increace employee account with paye ammount
                models.Transaction(debitAccount=paye, creditAccount=employee,
                        amount=payeAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
                #Move paye amount to SARS
                models.Transaction(debitAccount=employee, creditAccount=sars,
                        amount=payeAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            if uifAmount is not None:
                #Increace employee account with paye ammount
                models.Transaction(debitAccount=uif, creditAccount=employee,
                        amount=uifAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
                #Move paye amount to SARS
                models.Transaction(debitAccount=employee, creditAccount=sars,
                        amount=uifAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            else:
                uifAmount = Decimal(0.0)
            #Increace employee account with nett salary
            nett = grossAmount - payeAmount - uifAmount
            models.Transaction(debitAccount=salaries, creditAccount=employee,
                    amount=nett, date=date, recordedBy=request.user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Increace employee account with bonus amount
            if bonusAmount is not None:
                models.Transaction(debitAccount=bonusses, creditAccount=employee,
                        amount=bonusAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            return redirect(employee)
    return render(request, "sb/payslip_form.html", {'pform': pform, 'dform': dform})
      
