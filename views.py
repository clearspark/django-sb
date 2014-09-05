import csv
import datetime
from decimal import Decimal
import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from sb import models, forms
# Create your views here.

def check_perm(request, perm):
    if hasattr(request.user, 'bookie'):
        if getattr(request.user.bookie, perm):
            return True
    raise PermissionDenied()
    
def accounts_sum(accounts, begin=None, end=None):
    return sum([a.balance(begin, end) for a in accounts])

@login_required
def account_list(request):
    accounts = models.Account.objects.all()
    return render(request, "sb/account_list.html",
            {"accounts": accounts})

@login_required
def account_details(request, pk):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    account = get_object_or_404(models.Account, pk=pk)
    account.period_transactions = account.get_transactions(begin, end)
    account.period_dt_sum = account.dt_sum(begin, end)
    account.period_ct_sum = account.ct_sum(begin, end)
    account.period_balance = account.pretty_balance(begin, end)
    return render(request, "sb/account_detail.html", 
            {"account": account, 'dateform': dateform})

@login_required
def doc_list(request):
    from django.db.models import Min, Max
    docs = models.SourceDoc.objects.annotate(min_date=Min("transactions__date"))
    docs = docs.annotate(max_date=Max("transactions__date")).all()
    return render(request, "sb/doc_list.html", {"docs": docs})

@login_required
def doc_details(request, pk):
    doc = get_object_or_404(models.SourceDoc, pk=pk)
    return render(request, "sb/doc_detail.html", {"doc": doc})

@login_required
def trans_details(request, pk):
    trans = get_object_or_404(models.Transaction, pk=pk)
    return render(request, "sb/trans_detail.html", {"trans": trans})

@login_required
def trans_list(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    transactions = models.Transaction.objects.all()
    if begin is not None:
        transactions = transactions.filter(date__gte=begin)
        begin = begin.isoformat()
    if end is not None:
        transactions = transactions.filter(date__lte=end)
        end = end.isoformat()
    accountform = forms.AccountFilter(request.GET)
    if accountform.is_valid():
        debitAccounts = accountform.cleaned_data['debitAccount']
        creditAccounts = accountform.cleaned_data['creditAccount']
        if debitAccounts:
            transactions = transactions.filter(debitAccount__in=debitAccounts)
        if creditAccounts:
            transactions = transactions.filter(creditAccount__in=creditAccounts)
    total = transactions.aggregate(Sum('amount'))['amount__sum']
    return render(request, "sb/trans_list.html",
            {"transactions": transactions, 'dateform': dateform, 'begin': begin,
                'end': end, 'accountform': accountform, 'total': total})

@login_required
def trial_balance(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    def annotate(cat):
        accounts = list(models.Account.objects.filter(cat=cat).all())
        for a in accounts:
            a.period_dt_sum = a.dt_sum(begin, end)
            a.period_ct_sum = a.ct_sum(begin, end)
            a.period_balance = a.balance(begin, end)
        return accounts
    accGroups = [ {'cat': cat[1], 'accounts': annotate(cat[0])}
                for cat in models.ACCOUNT_CATEGORIES]
    for g in accGroups:
        g['total'] = sum([ a.period_balance for a in g['accounts']])
    accountDict = {"account_groups": accGroups, 'dateform': dateform}
    return render(request, "sb/trial_balance.html", accountDict)

@login_required
def add_payslip(request):
    check_perm(request, 'canAddPayslip')
    if request.method == "GET":
        pform = forms.PaySlipForm()
        dform = forms.SourceDocForm()
        rforms = forms.ReimbursementFormSet()
    elif request.method == "POST":
        pform = forms.PaySlipForm(request.POST)
        dform = forms.SourceDocForm(request.POST, request.FILES)
        rforms = forms.ReimbursementFormSet(request.POST)
        if pform.is_valid() and dform.is_valid() and rforms.is_valid():
            #Read data
            sourceDoc = dform.save(commit=False)
            sourceDoc.recordedBy=request.user
            sourceDoc.docType = 'payslip'
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
            sdl = models.Account.objects.get(name="SDL")
            sars = models.Account.objects.get(name="SARS")
            bonusses = models.Account.objects.get(name="Bonusses")
            #generate transactions
            if payeAmount:
                #Increace employee account with paye ammount
                models.Transaction(debitAccount=paye, creditAccount=employee,
                        amount=payeAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
                #Move paye amount to SARS
                models.Transaction(debitAccount=employee, creditAccount=sars,
                        amount=payeAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            else:
                payeAmount = Decimal('0.0')
            if uifAmount:
                #Increace employee account with paye ammount
                models.Transaction(debitAccount=uif, creditAccount=employee,
                        amount=uifAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
                #Move paye amount to SARS
                models.Transaction(debitAccount=employee, creditAccount=sars,
                        amount=uifAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
                #Add company contribution
                models.Transaction(debitAccount=uif, creditAccount=sars,
                        amount=uifAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()

            else:
                uifAmount = Decimal('0.0')
            #Increace employee account with nett salary
            nett = grossAmount - payeAmount - uifAmount
            models.Transaction(debitAccount=salaries, creditAccount=employee,
                    amount=nett, date=date, recordedBy=request.user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Add SDL transation
            sdlAmount = grossAmount / Decimal('100.00')
            models.Transaction(debitAccount=sdl, creditAccount=sars,
                    amount=sdlAmount, date=date, recordedBy=request.user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Increace employee account with bonus amount
            if bonusAmount:
                models.Transaction(debitAccount=bonusses, creditAccount=employee,
                        amount=bonusAmount, date=date, recordedBy=request.user,
                        sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            for rform in rforms:
                account = rform.cleaned_data.get('account', None)
                if account is not None:
                    models.Transaction(debitAccount=account,
                            creditAccount=employee, amount=rform.cleaned_data['amount'],
                            date=date, recordedBy=request.user, sourceDocument=sourceDoc,
                            comments="", isConfirmed = True).save()
            return redirect(sourceDoc)
    return render(request, "sb/payslip_form.html", 
            {'pform': pform, 'dform': dform, 'rforms': rforms})

import decimal
@login_required
def send_invoice(request):
    check_perm(request, 'canSendInvoice')
    if request.method == "GET":
        form = forms.SendInvoiceForm(initial={'date':datetime.date.today()})
    elif request.method == "POST":
        form = forms.SendInvoiceForm(request.POST)
        if form.is_valid():
            sourceDoc = models.SourceDoc()
            sourceDoc.number = models.get_new_invoice_nr()
            sourceDoc.recordedBy = request.user
            sourceDoc.comments = form.cleaned_data['comments']
            sourceDoc.docType = 'invoice-out'
            sourceDoc.save()
            sales = models.Account.objects.get(name='Sales')
            models.Transaction(
                debitAccount=form.cleaned_data['client'],
                creditAccount=sales,
                amount=form.cleaned_data['amount'],
                date=form.cleaned_data['date'],
                recordedBy=request.user,
                sourceDocument=sourceDoc,
                comments="",
                isConfirmed = True).save()
            if form.cleaned_data['vat']:
                vat = models.Account.objects.get(name='VAT')
                models.Transaction(
                    debitAccount=form.cleaned_data['client'],
                    creditAccount=vat,
                    amount=form.cleaned_data['amount'] * Decimal('0.14'),
                    date=form.cleaned_data['date'],
                    recordedBy=request.user,
                    sourceDocument=sourceDoc,
                    comments="",
                    isConfirmed = True).save()
            #Read data
            return redirect(sourceDoc)
    return render(request, "sb/send_invoice.html", 
            {'form': form})
    
@login_required
def get_invoice(request):
    check_perm(request, 'canReceiveInvoice')
    if request.method == "GET":
        tform = forms.GetInvoiceForm(initial={'date':datetime.date.today()})
        dform = forms.SourceDocForm()
    elif request.method == "POST":
        tform = forms.GetInvoiceForm(request.POST)
        dform = forms.SourceDocForm(request.POST, request.FILES)
        if tform.is_valid() and dform.is_valid():
            sourceDoc = dform.save(commit=False)
            sourceDoc.recordedBy = request.user
            sourceDoc.docType = 'invoice-in'
            sourceDoc.save()
            t1 = models.Transaction(
                debitAccount=tform.cleaned_data['spentOn'],
                creditAccount=tform.cleaned_data['vendor'],
                amount=tform.cleaned_data['amount'],
                date=tform.cleaned_data['date'],
                recordedBy=request.user,
                sourceDocument=sourceDoc,
                comments=tform.cleaned_data['comments'],
                isConfirmed = True).save()
            if tform.cleaned_data['vat']!='none':
                if tform.cleaned_data['vat'] == 'auto':
                    amount = tform.cleaned_data['amount'] * Decimal('0.14')
                elif tform.cleaned_data['vat']=='specify':
                    amount = tform.cleaned_data['VATAmount']
                vat = models.Account.objects.get(name='VAT')
                t2 = models.Transaction(
                    debitAccount=vat,
                    creditAccount=tform.cleaned_data['vendor'],
                    amount=amount,
                    date=tform.cleaned_data['date'],
                    recordedBy=request.user,
                    sourceDocument=sourceDoc,
                    comments="",
                    isConfirmed = True).save()
            #Read data
            return redirect(sourceDoc)
    return render(request, "sb/get_invoice.html", 
            {'tform': tform, 'dform': dform})

@login_required
def income_statement(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    salesIncomeAccounts = models.Account.objects.filter(name="sales").all()
    salesIncomeSum = - accounts_sum(salesIncomeAccounts, begin, end)
    sales = {"name": "Normal income", "accounts": salesIncomeAccounts, "sum": salesIncomeSum}
    otherIncomeAccounts = models.Account.objects.exclude(name="Sales").filter(cat="income").all()
    otherIncomeSum = - accounts_sum(otherIncomeAccounts, begin, end)
    other = {"name": "Other income", "accounts": otherIncomeAccounts, "sum": otherIncomeSum}
    expenseAccounts = models.Account.objects.filter(cat="expense").all()
    expenseSum = - accounts_sum(expenseAccounts, begin, end)
    expenses = {"name": "Expenses", "accounts": expenseAccounts, "sum": expenseSum}
    totalSum = salesIncomeSum + otherIncomeSum + expenseSum
    return render(request, "sb/income_statement.html", {"cats":[sales, other, expenses], "net": totalSum, 'dateform': dateform})

@login_required
def extract(request, dataType):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    dataTypes = ('transactions','trial balance')
    if dataType not in dataTypes:
        raise Http404
    if dataType == 'transactions':
        transactions = models.Transaction.objects.order_by('date')
        if begin:
            transactions = transactions.filter(date__gte=begin)
        if end:
            transactions = transactions.filter(date__lte=end)
        transactions = transactions.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Transaction_%s.csv"' %datetime.date.today().isoformat()
        writer = csv.writer(response, dialect='excel')
        writer.writerow(['Date', 'Debit account', 'Credit account', 'Amount', 'Comment', 'Document'])
        for t in transactions:
            writer.writerow( [t.date, t.debitAccount.long_name(), t.creditAccount.long_name(), t.amount, t.comments, t.sourceDocument.number if t.sourceDocument else ''] )
        return response
    if dataType == 'trial balance':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Trial_balance_%s.csv"' %datetime.date.today().isoformat()
        writer = csv.writer(response, dialect='excel')
        writer.writerow(['gl_code', 'Account name', 'Account type', 'Statement', 'Debit total', 'Credit total', 'Balance'])
        for a in models.Account.objects.order_by('gl_code').all():
            writer.writerow( [a.gl_code, a.long_name(), a.get_cat_display(), a.statement_type(), a.dt_sum(begin=begin, end=end), a.ct_sum(begin, end), a.balance(begin=begin, end=end)] )
        return response

def apply_interest(request):
    if request.method == "POST":
        form = forms.InterestForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            data = form.cleaned_data
            last_day = calendar.monthrange(data['year'], data['month'])[1]
            begin = datetime.date(data['year'], data['month'], 1)
            end = datetime.date(data['year'], data['month'], last_day)
            sourceDoc = models.SourceDoc(number=data['docNumber'],
                    recordedBy=request.user,
                    docType='other'
                    )
            print sourceDoc
            sourceDoc.save()
            for a in data['accounts']:
                balance = a.get_average_balance(begin, end)
                interest_amount = abs(balance * data['rate'] / Decimal("12.0"))
                print a, ':'
                print interest_amount
                print balance
                t = models.Transaction(debitAccount=data['expense'],
                        creditAccount=a,
                        date=data['date'],
                        amount=interest_amount,
                        recordedBy=request.user,
                        sourceDocument=sourceDoc)
                print t
                t.save()
            return redirect(sourceDoc)

    else:
        form = forms.InterestForm()
    return render(request, 'sb/generic_form.html', {'form': form, 'heading': "Apply Interest"})

