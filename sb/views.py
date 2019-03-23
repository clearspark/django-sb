import csv
import datetime
from decimal import Decimal
import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from sb import models, forms
# Create your views here.

def is_bookie(user):
    if not hasattr(user, 'bookie'):
        raise Http404
    return True

def check_perm(request, perm):
    if hasattr(request.user, 'bookie'):
        if getattr(request.user.bookie, perm):
            return True
    raise PermissionDenied()
    
def accounts_sum(accounts, begin=None, end=None, isConfirmed=True):
    return sum([a.balance(begin, end, isConfirmed) for a in accounts])

@user_passes_test(is_bookie)
def account_list(request):
    accounts = models.Account.objects.all()
    return render(request, "sb/account_list.html",
            {"accounts": accounts})

@user_passes_test(is_bookie)
def account_details(request, pk):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    account = get_object_or_404(models.Account, pk=pk)
    account.period_transactions = account.get_transactions(begin, end, True)
    account.period_dt_sum = account.dt_sum(begin, end, True)
    account.period_ct_sum = account.ct_sum(begin, end, True)
    account.period_balance = account.pretty_balance(begin, end, True)
    return render(request, "sb/account_detail.html", 
            {"account": account, 'dateform': dateform})

@user_passes_test(is_bookie)
def doc_list(request):
    from django.db.models import Min, Max
    docs = models.SourceDoc.objects.annotate(min_date=Min("transactions__date"))
    docs = docs.annotate(max_date=Max("transactions__date")).all()
    return render(request, "sb/doc_list.html", {"docs": docs})

@user_passes_test(is_bookie)
def doc_new(request):
    if request.method == 'POST':
        docForm = forms.SourceDocForm(request.POST, request.FILES)
        transFormSet = forms.TransactionFormSet(request.POST, prefix='tr')
        cctransFormSet = forms.CCTransactionFormSet(request.POST, prefix='cc')
        if docForm.is_valid() and transFormSet.is_valid() and cctransFormSet.is_valid():
            doc = docForm.save(commit=False)
            doc.recordedBy = request.user
            doc.save()
            transactions = transFormSet.save(commit=False)
            cctransactions = cctransFormSet.save(commit=False)
            for t in transactions:
                t.sourceDocument = doc
                t.recordedBy = request.user
                t.save()
            for cct in cctransactions:
                cct.sourceDocument = doc
                cct.recordedBy = request.user
                cct.save()
            return redirect(doc)
        else:
            #for is invlaid, display again
            pass
    else:
        docForm = forms.SourceDocForm()
        transFormSet = forms.TransactionFormSet(queryset=models.Transaction.objects.none(), prefix='tr')
        cctransFormSet = forms.CCTransactionFormSet(queryset=models.CCTransaction.objects.none(), prefix='cc')
    return render(request, 'sb/doc_new.html',
            {'docForm': docForm, 
            'transFormSet': transFormSet, 
            'cctransFormSet': cctransFormSet})

@user_passes_test(is_bookie)
def series_list(request):
    series = models.TransactionSeries.objects
    series = series.annotate(t_count=models.models.Count('transactions', distinct=True))
    series = series.annotate(cct_count=models.models.Count('cctransactions', distinct=True))
    return render(request, 'sb/series_list.html', {'series': series})


@user_passes_test(is_bookie)
def series_details(request, pk):
    series = get_object_or_404(models.TransactionSeries, pk=pk)
    return render(request, 'sb/series_details.html', {'series': series})

@user_passes_test(is_bookie)
def series_new(request):
    c = {}
    if request.method == 'POST':
        seriesForm = forms.TransactionSeriesForm(request.POST)
        tbpfs = forms.TransactionBluePrintFormSet(request.POST, prefix='tbp')
        if seriesForm.is_valid() and tbpfs.is_valid():
            if 'create_series' in request.POST:
                # Create new series
                series = seriesForm.save()
                blueprints = tbpfs.save(commit=False)
                for b in blueprints:
                    b.series = series
                    b.save()
                transactions = series.get_transactions(blueprints)
                for t in transactions:
                    t.recordedBy = request.user
                    t.save()
                    if t.transactionType == 'normal':
                        series.transactions.add(t)
                        for scenario in series.scenarios.all():
                            scenario.transactions.add(t)
                    else:
                        series.cctransactions.add(t)
                        for scenario in series.scenarios.all():
                            scenario.cctransactions.add(t)
                series.save()
                for s in series.scenarios.all():
                    s.save()

                return redirect('trialbalance')
            else:
                # Create preview information and display again
                series = seriesForm.save(commit=False)
                blueprints = tbpfs.save(commit=False)
                transactions = series.get_transactions(blueprints)
                c['transactions'] = transactions
                c['has_preview_data'] = True
        else:
            # display form again with error message
            pass
    else:
        seriesForm = forms.TransactionSeriesForm()
        tbpfs = forms.TransactionBluePrintFormSet(prefix='tbp', queryset=models.TransactionBlueprint.objects.none())
    c.update({'seriesForm': seriesForm, 'tbpfs': tbpfs})
    return render(request, 'sb/series_new.html', c)

@user_passes_test(is_bookie)
def doc_details(request, pk):
    doc = get_object_or_404(models.SourceDoc, pk=pk)
    return render(request, "sb/doc_detail.html", {"doc": doc})

@user_passes_test(is_bookie)
def trans_details(request, pk):
    trans = get_object_or_404(models.Transaction, pk=pk)
    return render(request, "sb/trans_detail.html", {"trans": trans})

@user_passes_test(is_bookie)
def trans_list(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    transactions = models.Transaction.objects.filter(isConfirmed=True)
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

@user_passes_test(is_bookie)
def trial_balance(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    def annotate(cat):
        accounts = list(models.Account.objects.filter(cat=cat).all())
        for a in accounts:
            a.period_dt_sum = a.dt_sum(begin, end, True)
            a.period_ct_sum = a.ct_sum(begin, end, True)
            a.period_balance = a.balance(begin, end, True)
        return accounts
    accGroups = [ {'cat': cat[1], 'accounts': annotate(cat[0])}
                for cat in models.ALL_ACCOUNT_CATEGORIES]
    for g in accGroups:
        g['total'] = sum([ a.period_balance for a in g['accounts']])
    context = {"account_groups": accGroups, 'dateform': dateform, 'begin':begin, 'end': end}
    return render(request, "sb/trial_balance.html", context)

@user_passes_test(is_bookie)
def add_payslip_0(request):
    check_perm(request, 'canAddPayslip')
    employees = models.Employee.objects.filter(isActive=True)
    return render(request, "sb/add_payslip_0.html", {'employees': employees})

@user_passes_test(is_bookie)
def add_payslip_1(request, employee_pk):
    check_perm(request, 'canAddPayslip')
    employee = get_object_or_404(models.Employee, pk=employee_pk)
    if request.method == "GET":
        #Payslip form
        past_payslips = models.Payslip.objects\
                .filter(
                    employee=employee)\
                .order_by(
                    '-transactions__date')
        if past_payslips.exists():
            last_payslip = past_payslips[0]
            prev_date = last_payslip.date
            y, m = divmod(12 * prev_date.year + prev_date.month + 2, 12)
            suggested_date = datetime.date(year=y, month=m, day=1) - datetime.timedelta(days=1)
        else:
            nm = datetime.date.today() + datetime.timedelta(days=14)
            suggested_date = datetime.date(year=nm.year, month=nm.month, day=1) - datetime.timedelta(days=1)
        doc_number = 'ps_{initials}_{year}_{month}'.format(
                initials=employee.initials,
                year=suggested_date.year,
                month=suggested_date.month)
        pform = forms.PaySlipForm(
                initial={'number': doc_number,
                         'date': suggested_date})
        
        #Cost centre contribution form
        cccforms = forms.CCCForms(
                initial = [ 
                    {'costCentre': a.department.costCentre, 'fraction': a.timeFraction} 
                    for a in employee.current_appointments()]
                )
    elif request.method == "POST":
        pform = forms.PaySlipForm(request.POST, request.FILES)
        cccforms = forms.CCCForms(request.POST)
        if pform.is_valid() and cccforms.is_valid():
            payslip = pform.save(commit=False)
            payslip.recordedBy = request.user
            payslip.docType = 'payslip'
            payslip.employee = employee
            payslip.save()
            try:
                payslip.make_transactions(request.user)
                for ccc in cccforms.cleaned_data:
                    if 'costCentre' in ccc:
                        payslip.add_cost_centre_contribution(ccc['costCentre'], ccc['fraction'], request.user)
                success = True
            except Exception as e:
                payslip.delete()
                messages.error(request, "Unable to create transactions. Payslip not added!")
                success = False
                from django.conf import settings
                if settings.DEBUG:
                    raise e
            if success:
                return redirect(payslip)
    return render(request, "sb/add_payslip_1.html", 
            {'employee': employee, 'pform': pform, 'cccforms': cccforms})

import decimal
@user_passes_test(is_bookie)
def send_invoice(request):
    check_perm(request, 'canSendInvoice')
    if request.method == "GET":
        form = forms.SendInvoiceForm(initial={'date':datetime.date.today()})
        lineForms = forms.InvoiceLinesFormSet(queryset=models.InvoiceLine.objects.none())
    elif request.method == "POST":
        #Get client, date, invoice lines
        form = forms.SendInvoiceForm(request.POST)
        lineForms = forms.InvoiceLinesFormSet(request.POST)
        if form.is_valid() and lineForms.is_valid():
            client = form.cleaned_data['client']
            sourceDoc = models.Invoice()
            sourceDoc.number = client.get_new_invoice_nr()
            sourceDoc.recordedBy = request.user
            sourceDoc.comments = form.cleaned_data['comments']
            sourceDoc.invoiceDate = form.cleaned_data['date']
            sourceDoc.clientSummary = form.cleaned_data['clientSummary']
            sourceDoc.docType = 'invoice-out'
            sourceDoc.client = client
            sourceDoc.isQuote = form.cleaned_data.get('isQuote', False)
            sourceDoc.save()
            for lineItem in lineForms.save(commit=False):
                #lineItem = l.save(commit=False)
                lineItem.invoice = sourceDoc
                lineItem.save()
            sourceDoc.html = sourceDoc.make_html()
            sourceDoc.save()
            if not sourceDoc.isQuote:
                sourceDoc.make_transactions(form.cleaned_data['department'], request.user)
            return redirect(sourceDoc)
    return render(request, "sb/send_invoice.html", 
            {'form': form, 'lineforms': lineForms})

@user_passes_test(is_bookie)
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
            models.CCTransaction(
                debitAccount=tform.cleaned_data['spentOn'],
                creditAccount=tform.cleaned_data['department'].costCentre,
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
                vat = models.Account.objects.get(name='Input VAT')
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

@user_passes_test(is_bookie)
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

@user_passes_test(is_bookie)
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
        writer.writerow(['Date', 'Debit account', 'Debit account code', 'Credit account', 'Credit account code', 'Amount', 'Comment', 'Document'])
        for t in transactions:
            writer.writerow( [t.date, t.debitAccount.long_name(), t.debitAccount.gl_code, t.creditAccount.long_name(), t.creditAccount.gl_code, t.amount, t.comments, t.sourceDocument.number if t.sourceDocument else ''] )
        return response
    if dataType == 'trial balance':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Trial_balance_%s.csv"' %datetime.date.today().isoformat()
        writer = csv.writer(response, dialect='excel')
        writer.writerow(['gl_code', 'Account name', 'Account type', 'Statement', 'Debit total', 'Credit total', 'Balance'])
        for a in models.Account.objects.order_by('gl_code').all():
            writer.writerow( [a.gl_code, a.long_name(), a.get_cat_display(), a.statement_type(), a.dt_sum(begin=begin, end=end), a.ct_sum(begin, end), a.balance(begin=begin, end=end)] )
        return response

@user_passes_test(is_bookie)
def apply_interest(request):
    check_perm(request, 'canApplyInterest')
    if request.method == "POST":
        form = forms.InterestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            last_day = calendar.monthrange(data['year'], data['month'])[1]
            begin = datetime.date(data['year'], data['month'], 1)
            end = datetime.date(data['year'], data['month'], last_day)
            sourceDoc = models.SourceDoc(number=data['docNumber'],
                    recordedBy=request.user,
                    docType='other'
                    )
            sourceDoc.save()
            for a in data['accounts']:
                balance = a.get_average_balance(begin, end)
                interest_amount = abs(balance * data['rate'] / Decimal("12.0"))
                t = models.Transaction(debitAccount=data['expense'],
                        creditAccount=a,
                        date=data['date'],
                        amount=interest_amount,
                        recordedBy=request.user,
                        sourceDocument=sourceDoc,
                        isConfirmed=True)
                t.save()
            return redirect(sourceDoc)

    else:
        form = forms.InterestForm()
    return render(request, 'sb/generic_form.html', {'form': form, 'heading': "Apply Interest"})

@user_passes_test(is_bookie)
def client_account_statement(request):
    form = forms.ClientStatementForm(request.GET or None)
    if form.is_valid():
        client = form.cleaned_data['client']
        if not client.adminGoup.user_set.filter(pk=request.user.pk).exists():
            raise PermissionDenied
        statementDate = form.cleaned_data['statementDate']
        startDate = form.cleaned_data['startDate']
        statement = models.Statement(client, startDate, statementDate)
        return HttpResponse(statement.make_html())
    else:
        return render(request, 'sb/client_statements_menu.html', {'form': form})
    
@user_passes_test(is_bookie)
def view_invoice(request, invoice_nr):
    invoice = get_object_or_404(models.Invoice, number=invoice_nr)
    client = invoice.client
    if not client.adminGoup.user_set.filter(pk=request.user.pk).exists():
        raise PermissionDenied
    if request.GET.get('generate', False):
        return HttpResponse(invoice.make_html())
    else:
        return HttpResponse(invoice.html)

@user_passes_test(is_bookie)
def regen_invoice(request, invoice_nr):
    invoice = get_object_or_404(models.Invoice, number=invoice_nr)
    client = invoice.client
    if not client.adminGoup.user_set.filter(pk=request.user.pk).exists():
        raise PermissionDenied
    invoice.html = invoice.make_html()
    invoice.save()
    return redirect(invoice)

@user_passes_test(is_bookie)
def claim_edit(request, pk=None):
    if pk is not None:
        claim = models.ExpenseClaim.objects.get(pk=pk)
        role = claim.get_role(request.user)
        if role == 'unrelated':
            raise PermissionDenied("You are not authorised to edit this expense claim.")
    else:
        claim = None
    if request.method == 'POST':
        form = forms.NewExpenseClaimForm(request.POST, instance=claim)
        if form.is_valid():
            claim = form.save(commit=False)
            employee = models.Employee.objects.get(user=request.user)
            claim.claimant = employee
            claim.save()
            return redirect(claim)
    else:
        if pk is None:
            form = forms.NewExpenseClaimForm()
        else:
            form = forms.NewExpenseClaimForm(instance=claim)
    return render(request, 'sb/generic_form.html', {'form': form, 'heading': 'New claim'})

@user_passes_test(is_bookie)
def claim_add_supporting_docs(request, pk):
    claim = get_object_or_404(models.ExpenseClaim, pk=pk)
    role = claim.get_role(request.user)
    if role == 'unrelated':
        raise PermissionDenied("You are not authorised to edit this expense claim.")
    if request.method == 'POST':
        form = forms.SupportingDocForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.subject = claim
            doc.save()
            return redirect(claim)
    else:
        form = forms.SupportingDocForm()
    return render(request, 'sb/generic_form.html',
            {'form': form, 'has_files': True, 'heading': 'Adding supporting document'})
    
@user_passes_test(is_bookie)
def claim_detail(request, pk):
    claim = get_object_or_404(models.ExpenseClaim, pk=pk)
    role = claim.get_role(request.user)
    return render(request, 'sb/claim_detail.html', {'claim': claim, 'role': role})

@user_passes_test(is_bookie)
def submit_claim(request, pk):
    claim = get_object_or_404(models.ExpenseClaim, pk=pk)
    role = claim.get_role(request.user)
    if role != 'claimant':
        raise PermissionDenied("You are not authorised to edit this expense claim.")
    claim.submit()
    messages.info(request, "Your claim has been submitted for review")
    return redirect(claim)

@user_passes_test(is_bookie)
def review_claim(request, pk):
    claim = get_object_or_404(models.ExpenseClaim, pk=pk)
    role = claim.get_role(request.user)
    if role != 'reviewer':
        raise PermissionDenied("You are not authorised to review this expense claim.")
    if request.method == 'POST':
        form = forms.ExpenseClaimReviewForm(request.POST, instance=claim)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.reviewedBy = models.Employee.objects.get(user=request.user)
            claim.reviewDate = datetime.date.today()
            claim.save()
            return redirect(claim)
    else:
        form = forms.ExpenseClaimReviewForm(instance=claim)
    return render(
            request, 'sb/generic_form.html',
            {'form': form, 'has_files': True, 'instance': claim,
                'heading': 'Reviewing claim: %s' %claim.__str__()},
        )

@user_passes_test(is_bookie)
def claim_list(request):
    claims = models.ExpenseClaim.objects.all()
    return render(request, 'sb/expense_claim_list.html', {'objects': claims})

@user_passes_test(is_bookie)
def expense_chart(request):
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()

    expenses = models.Account.objects.filter(cat='expense').all()
    for e in expenses:
        e.period_balance = abs(e.balance(begin=begin, end=end))
    
    return render(
            request, 
            'sb/expense_chart.html',
            {'dateform': dateform, 
            'expenses': expenses}
        )

@user_passes_test(is_bookie)
def values_over_time(request):
    c = {}
    dateform = forms.DateRangeFilter(request.GET)
    begin, end = dateform.get_range()
    if 'submit' in request.GET:
        form = forms.VOTForm(request.GET)
        if form.is_valid():
            c['show_report'] = True
            c['accounts'] = accounts = form.cleaned_data['accounts']
            for a in accounts:
                transactions = a.get_transactions(end=end).all()
                data = []
                balance = Decimal('0.00')
                date = None
                for t in  transactions:
                    if t.date != date:
                        if date is not None and date >= begin:
                            data.append((date, balance,))
                        date = t.date
                    if t.debitAccount == a:
                        balance += t.amount
                    else:
                        balance -= t.amount
                data.append((date, balance,))
                a.balance_series = data
    else:
        form = forms.VOTForm()

    c.update({'dateform': dateform, 'form': form})
    return render(
            request, 
            'sb/values_over_time.html',
            c
        )
