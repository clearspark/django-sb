#vim: set foldmethod=indent

from datetime import timedelta
import datetime

from decimal import Decimal

from django.db import models
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

#from mptt.models import MPTTModel, TreeForeignKey

GAAP_ACCOUNT_CATEGORIES = (("equity", "Equity"), ("asset", "Asset"), ("liability", "Liability"), ("income", "Income"), ("expense", "Expense"),)
INTERNAL_ACCOUNT_CATEGORIES = (("cost_centre", "Cost centre"),)
ALL_ACCOUNT_CATEGORIES = GAAP_ACCOUNT_CATEGORIES + INTERNAL_ACCOUNT_CATEGORIES
INCOME_STATEMENT_CATS = ('income', 'expense',)
BALANCE_SHEET_CATS = ('equity', 'asset', 'liability',)
GAAP_CATS = INCOME_STATEMENT_CATS + BALANCE_SHEET_CATS
INTERNAL_SHEET_CATS = ('cost_centre',)

def url_to_edit_object(object):
    url = reverse('admin:%s_%s_change' %(object._meta.app_label,  object._meta.model_name),  args=[object.id] )
    return url

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    cat = models.CharField(max_length=200, choices=ALL_ACCOUNT_CATEGORIES)
    gl_code = models.CharField(max_length=20, blank=True)
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True)
    class Meta:
        ordering = ["name"]
    def long_name(self):
        if self.parent:
            return self.parent.__str__()+" > "+self.name
        else:
            return self.name
    def long_href(self):
        if self.parent:
            return self.parent.href()+"&gt"+self.href()
        else:
            return self.href()
    def __str__(self):
        return self.long_name()
    def transactions(self):
        if self.cat in GAAP_CATS:
            return Transaction.objects.filter( models.Q(debitAccount=self) | models.Q(creditAccount=self)).order_by("date")
        else:
            return CCTransaction.objects.filter( models.Q(debitAccount=self) | models.Q(creditAccount=self)).order_by("date").all()
    def get_transactions(self, begin=None, end=None, isConfirmed=None):
        transactions = self.transactions()
        if begin is not None:
            transactions = transactions.filter(date__gte=begin)
        if end is not None:
            transactions = transactions.filter(date__lte=end)
        if isConfirmed is not None:
            transactions = transactions.filter(isConfirmed=isConfirmed)
        return transactions
    def get_debits(self, begin=None, end=None, isConfirmed=None):
        if self.cat in GAAP_CATS:
            debits = self.debits
        else:
            debits = self.cc_debits
        if begin is not None:
            debits = debits.filter(date__gte = begin)
        if end is not None:
            debits = debits.filter(date__lte = end)
        if isConfirmed is not None:
            debits = debits.filter(isConfirmed=isConfirmed)
        return debits
    def get_credits(self, begin=None, end=None, isConfirmed=None):
        if self.cat in GAAP_CATS:
            credits = self.credits
        else:
            credits = self.cc_credits
        if begin is not None:
            credits = credits.filter(date__gte = begin)
        if end is not None:
            credits = credits.filter(date__lte = end)
        if isConfirmed is not None:
            credits = credits.filter(isConfirmed=isConfirmed)
        return credits
    def dt_sum(self, *args, **kwargs):
        return sum(self.get_debits(*args, **kwargs).all().values_list("amount", flat=True))
    def ct_sum(self,  *args, **kwargs):
        return sum(self.get_credits(*args, **kwargs).all().values_list("amount", flat=True))
    def balance(self, *args, **kwargs):
        return self.dt_sum(*args, **kwargs) - self.ct_sum(*args, **kwargs)
    def ct_balance(self, *args, **kwargs):
        return -self.balance(*args, **kwargs)
    def pretty_balance(self, *args, **kwargs):
        balance = self.balance(*args, **kwargs)
        if balance >= 0:
            return "Dr {}".format(balance)
        else:
            return "Cr {}".format(-balance)
    def get_average_balance(self, begin, end):
        num_days = (end - begin).days + 1
        avg_balance = self.balance(end=(begin-timedelta(days=1)))
        debits = self.get_debits(begin, end)
        credits = self.get_credits(begin, end)
        for d in debits:
            avg_balance += (d.amount * (end - d.date).days) / num_days
        for c in credits:
            avg_balance -= (c.amount * (end - c.date).days) / num_days
        return avg_balance
    def dt_count(self, *args, **kwargs):
        return self.get_debits(*args, **kwargs).all().count()
    def ct_count(self, *args, **kwargs):
        return self.get_credits(*args, **kwargs).all().count()
    def t_count(self, *args, **kwargs):
        return self.get_transactions(*args, **kwargs).count()
    def get_absolute_url(self):
        return reverse("account-details", kwargs={"pk": self.pk})
    def href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.name)
    def statement_type(self):
        if self.cat in INCOME_STATEMENT_CATS:
            return 'Income statement'
        elif self.cat in BALANCE_SHEET_CATS:
            return 'Balance sheet'
        else:
            return None

class Client(models.Model):
    account = models.ForeignKey('Account')
    adminGoup = models.ForeignKey('auth.Group')
    displayName = models.CharField(max_length=100)
    invoiceTemplate = models.TextField(blank=True, default='{% include "sb/default_invoice_template.html" %}')
    statementTemplate = models.TextField(blank=True)
    invoiceSuffix = models.CharField(max_length=12, unique=True)
    invoiceOffset = models.IntegerField(default=0, help_text='''The invoice number will be increaced by this number.
    The reason this is needed is that not all invoices in the database are explicitly represented as such and this ''' )
    address = models.TextField(help_text="This will be used for generating invoices and statements. HTML tags can be used. Should include Company name, registration, VAT nr etc.")
    def __str__(self):
        return self.displayName
    def get_new_invoice_nr(self):
        num = self.invoice_set.count() + self.invoiceOffset + 1
        return "CS%04d-%s" %(num, self.invoiceSuffix)

def source_doc_file_path(instance, filename):
    return "sb/src_docs/{}/{}".format(instance.number, filename)
class SourceDoc(models.Model):
    number = models.CharField(max_length=40, unique=True, help_text="Document number")
    electronicCopy = models.FileField(upload_to=source_doc_file_path, blank=True, null=True, verbose_name="Electronic copy")
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    comments = models.TextField(blank=True, help_text="Any comments/extra info/meta data about this doc.")
    docType = models.CharField(max_length=20, choices=(
        ('bank-statement', 'Bank statement'),
        ('invoice-out', 'Outbound invoice'),
        ('invoice-in', 'Inbound invoice'),
        ('payslip', 'Payslip'),
        ('other', 'Other')),
        help_text='The type of document being recorded/created')
    def __str__(self):
        return str(self.number)
    def transaction_count(self):
        return self.transactions.all().count()
    def get_absolute_url(self):
        return reverse("doc-details", kwargs={"pk": self.pk})
    def href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.number)
    def has_file(self):
        if self.electronicCopy:
            return True
        else:
            return False
    def edit_url(self):
        if hasattr(self, 'invoice'):
            return url_to_edit_object(self.invoice)
        if hasattr(self, 'payslip'):
            return url_to_edit_object(self.payslip)
        else:
            return url_to_edit_object(self)

#class ReimburseMent(models.Model):
#    payslip = models.ForeignKey('Payslip')
#    expense = models.ForeignKey('Account')
#    amount = models.Decimal(max_digits=16, decimal_places=2)

class Payslip(SourceDoc):
    employee = models.ForeignKey('Employee')
    date = models.DateField()
    gross = models.DecimalField(max_digits=16, decimal_places=2)
    uif = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    paye = models.DecimalField(max_digits=16, decimal_places=2, default=Decimal('0.00'))
    def make_transactions(self, user):
        sourceDoc = self
        employee = self.employee.account
        date = self.date
        grossAmount = self.gross
        payeAmount = self.paye
        uifAmount = self.uif
        salaries = Account.objects.get(name="Salaries")
        paye = Account.objects.get(name="PAYE")
        uif = Account.objects.get(name="UIF")
        sdl = Account.objects.get(name="SDL")
        sars = Account.objects.get(name="SARS - PAYE")
        #Initiate tracking variable
        costToCompany = grossAmount
        if self.paye:
            #Increace employee account with paye ammount
            Transaction(debitAccount=paye, creditAccount=employee,
                    amount=payeAmount, date=date, recordedBy=user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Move paye amount to SARS
            Transaction(debitAccount=employee, creditAccount=sars,
                    amount=payeAmount, date=date, recordedBy=user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
        else:
            payeAmount = Decimal('0.00')
        if uifAmount:
            #Increace employee account with paye ammount
            Transaction(debitAccount=uif, creditAccount=employee,
                    amount=uifAmount, date=date, recordedBy=user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Move paye amount to SARS
            Transaction(debitAccount=employee, creditAccount=sars,
                    amount=uifAmount, date=date, recordedBy=user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            #Add company contribution
            Transaction(debitAccount=uif, creditAccount=sars,
                    amount=uifAmount, date=date, recordedBy=user,
                    sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
            costToCompany += uifAmount
        else:
            uifAmount = Decimal('0.00')
        #Increace employee account with nett salary
        nett = grossAmount - payeAmount - uifAmount
        Transaction(debitAccount=salaries, creditAccount=employee,
                amount=nett, date=date, recordedBy=user,
                sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
        #Add SDL transation
        sdlAmount = grossAmount / Decimal('100.00')
        Transaction(debitAccount=sdl, creditAccount=sars,
                amount=sdlAmount, date=date, recordedBy=user,
                sourceDocument=sourceDoc, comments="", isConfirmed = True).save()
        costToCompany += sdlAmount
    def add_cost_centre_contribution(self, costCentre, fraction, user, comments=""):
        salaries = Account.objects.get(name="Salaries")
        amount = self.cost_to_company() * fraction
        CCTransaction(debitAccount=salaries, creditAccount=costCentre,
                    amount=amount, date=self.date, recordedBy=user,
                    sourceDocument=self, comments=comments, isConfirmed=True).save()
    def cost_to_company(self):
        return self.gross * Decimal('1.010') + self.uif

class Invoice(SourceDoc):
    client = models.ForeignKey('Client')
    isQuote = models.BooleanField(default=False)
    html = models.TextField(blank=True)
    invoiceDate = models.DateField()
    finalized = models.BooleanField(default=False)
    clientSummary = models.CharField(max_length=200,
            help_text='One or two sentence description of what invoice is for.  Will shown on invoice above line items. Possibly on statements.')
    def __str__(self):
        return self.number
    def get_total_excl(self):
        return self.invoiceline_set.aggregate(models.Sum('amount'))['amount__sum']
    def get_total_vat(self):
        return self.invoiceline_set.aggregate(models.Sum('vat'))['vat__sum']
    def get_total_incl(self):
        return self.get_total_excl() + self.get_total_vat()
    def make_html(self):
        t = Template(self.client.invoiceTemplate)
        c = Context({'invoice': self, 'STATIC_URL': settings.STATIC_URL})
        return t.render(c)
    def make_transactions(self, department, user):
        sales = Account.objects.get(name='Sales')
        amount = self.get_total_excl()
        Transaction(
                debitAccount=self.client.account,
                creditAccount=sales,
                amount=amount,
                date=self.invoiceDate,
                recordedBy=user,
                sourceDocument=self,
                comments="",
                isConfirmed = True).save()
        cc_amount = amount - (amount * department.invoiceDeductionFraction)
        CCTransaction(
                debitAccount=department.costCentre,
                creditAccount=sales,
                amount=cc_amount,
                date=self.invoiceDate,
                recordedBy=user,
                sourceDocument=self,
                comments="",
                isConfirmed = True).save()
        CSP=Department.objects.get(shortName="CSP")
        CCTransaction(debitAccount=CSP.costCentre,
                creditAccount=sales,
                amount= amount - cc_amount,
                date=self.invoiceDate,
                recordedBy=user,
                sourceDocument=self,
                comments="",
                isConfirmed=True).save()
        vat_amount = self.get_total_vat()
        if vat_amount > 0:
            vat = Account.objects.get(name='Output VAT')
            Transaction(
                debitAccount=self.client.account,
                creditAccount=vat,
                amount=vat_amount,
                date=self.invoiceDate,
                recordedBy=user,
                sourceDocument=self,
                comments="",
                isConfirmed = True).save()

class InvoiceLine(models.Model):
    invoice = models.ForeignKey('Invoice')
    description = models.CharField(max_length=1000)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    vat = models.DecimalField(max_digits=16, decimal_places=2)
    class Meta:
        ordering = ['pk']

class TransactionParent(models.Model):
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    date = models.DateField()
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    comments = models.TextField(blank=True)
    isConfirmed = models.BooleanField(default=True)
    series = models.ForeignKey('TransactionSeries', null=True, blank=True)
    class Meta:
        ordering = ["date", "pk"]
        abstract = True
    def date_href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.date)
    def get_absolute_url(self):
        return reverse("transaction-details", kwargs={"pk": self.pk})
    def __str__(self):
        return "{} {}:{} {}".format(self.date, self.debitAccount, self.creditAccount, self.amount)

class Transaction(TransactionParent):
    debitAccount = models.ForeignKey("Account", related_name="debits")
    creditAccount = models.ForeignKey("Account", related_name="credits")
    sourceDocument = models.ForeignKey(SourceDoc, related_name="transactions", blank=True, null=True)

class CCTransaction(TransactionParent):
    debitAccount = models.ForeignKey("Account", related_name="cc_debits")
    creditAccount = models.ForeignKey("Account", related_name="cc_credits")
    sourceDocument = models.ForeignKey(SourceDoc, related_name="cc_transactions", blank=True, null=True)

def asset_image_file_path(instance, filename):
    return "sb/assets/{}/{}".format(instance.number, filename)
class Asset(models.Model):
    number = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    location = models.TextField()
    image = models.FileField("Optional: photo of asset", upload_to=asset_image_file_path, blank=True, null=True)
    cost = models.DecimalField(max_digits=16, decimal_places=2)
    accDepreciation = models.DecimalField(max_digits=16, decimal_places=2)
    carryingValue = models.DecimalField(max_digits=16, decimal_places=2)
    acquisitionTransaction = models.ForeignKey('Transaction')
    usefulLife = models.IntegerField("Usefull lifespan in months")
    category = models.CharField("Asset category", max_length=50, choices=(('land', 'Land'), ('equipment', 'Equipment')))
    residualValue = models.DecimalField(max_digits=16, decimal_places=2,
            help_text="Estimated resale value of asset in current condition on current date.")
    disposalDate = models.DateField(null=True, blank=True)
    disposalValue = models.DecimalField(max_digits=16, decimal_places=2)
    
class Bookie(models.Model):
    user = models.OneToOneField('auth.User', related_name='bookie')
    canSendInvoice = models.BooleanField(default=False)
    canReceiveInvoice = models.BooleanField(default=False)
    canAddPayslip = models.BooleanField(default=False)
    canApplyInterest = models.BooleanField(default=False)
    def __str__(self):
        return self.user.get_full_name()

class Department(models.Model):
    longName = models.CharField(max_length=255)
    shortName = models.CharField(max_length=8)
    minMonthlyDeduction = models.DecimalField(max_digits=16, decimal_places=2)
    invoiceDeductionFraction = models.DecimalField(max_digits=4, decimal_places=4)
    costCentre = models.ForeignKey('Account', limit_choices_to={'cat__in': INTERNAL_SHEET_CATS})
    description = models.TextField()
    expenseReviewers = models.ManyToManyField('Employee')
    def __str__(self):
        return self.shortName

class Employee(models.Model):
    user = models.ForeignKey('auth.User')
    initials = models.CharField(max_length=5)
    account = models.ForeignKey(Account)
    isActive = models.BooleanField(help_text='Is employee currently working?')
    def __str__(self):
        return self.user.get_full_name()
    def current_appointments(self, date=None):
        if date is None:
            date = datetime.date.today()
        return self.appointment_set.filter(startDate__lte=date, endDate__gte=date).all()

class Appointment(models.Model):
    employee = models.ForeignKey(Employee)
    title = models.CharField(max_length=250)
    department = models.ForeignKey(Department)
    startDate = models.DateField()
    endDate = models.DateField()
    timeFraction = models.DecimalField(max_digits=5, decimal_places=4)

def supporting_doc_file_path(instance, filename):
    return "sb/src_docs/{}/{}".format(instance.created.date().isoformat(), filename)
class SupportingDoc(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subject = GenericForeignKey('content_type', 'object_id')
    description = models.CharField(
            max_length=250, 
            help_text='''Brief description of document, what it is and what it says.
                         Example: "Invoice showing expense incurred"''')
    document = models.FileField(
            upload_to=supporting_doc_file_path, 
            verbose_name="File")

class ExpenseClaim(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    claimant = models.ForeignKey('Employee', related_name='expenseClaimsMade')
    department = models.ForeignKey('Department')
    claimAmount = models.DecimalField(max_digits=16, decimal_places=2)
    claimComments = models.TextField(blank=True)
    submitted = models.BooleanField(default=False)
    reviewDate = models.DateTimeField(null=True, blank=True, editable=False)
    reviewedBy = models.ForeignKey('Employee', related_name='expenseClaimsReviewd', null=True, blank=True)
    reviewComments = models.TextField(blank=True)
    approvedAmount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    supportingDoc_set = GenericRelation(SupportingDoc, related_query_name='expenseClaims')
    def __str__(self):
        return '{claimant}: {amount} ({date})'.format(
                claimant=self.claimant,
                amount=self.claimAmount,
                date=self.created.date(),
                )
    def get_absolute_url(self):
        return reverse('claim-detail', kwargs={'pk': self.pk})
    def submit(self):
        '''Sends email to potential reviewer and marks claim for review'''
        pass
    def add_supporting_doc(self, doc):
        '''Adds a supporting document to the claim'''
        pass
    def get_role(self, user):
        if self.claimant.user == user:
            return 'claimant'
        elif self.department.expenseReviewers.filter(pk=user.pk).exists():
            return 'reviewer'
        else:
            return 'unrelated'
    def status(self):
        if not self.submitted:
            return 'draft'
        if self.submitted and self.reviewedBy is None:
            return 'submitted'
        if self.reviewedBy is not None:
            return 'reviewed'
        return 'unknown'
    def submit(self):
        self.submitted = True
        self.save()

    
#NON-DJANGO models
class StatementTransaction(object):
    def __init__(self, reference, date, description, debit, credit, balance):
        self.reference = reference
        self.date = date
        self.description = description
        self.debit = debit
        self.credit = credit
        self.balance = balance

class Statement(object):
    def __init__(self, client, startDate, statementDate):
        self.client = client
        self.startDate = startDate
        self.statementDate = statementDate
        self.transactions = None
        self.startingBalance = self.client.account.balance(end=self.startDate - timedelta(days=1))
        self.endingBalance = self.client.account.balance(end=self.statementDate)
        self.debtAge = None
        self.get_transactions()
        self.calculate_debt_age()
    def get_transactions(self):
        account = self.client.account
        self.transactions = []
        self.transactions.append(StatementTransaction(reference='', date=self.startDate,
            description= 'Balance carried over', debit='', credit='', balance=self.startingBalance))
        transactions = account.get_transactions(begin=self.startDate, end=self.statementDate)
        balance = self.startingBalance
        for t in transactions:
            if t.debitAccount == account:
                balance += t.amount
                self.transactions.append(
                        StatementTransaction(t.sourceDocument.number, t.date,
                            t.comments, t.amount, '', balance)
                        )
            else:
                balance -= t.amount
                self.transactions.append(
                        StatementTransaction(t.sourceDocument.number, t.date,
                            t.comments, '', t.amount, balance))
    def calculate_debt_age(self):
        account = self.client.account
        debits = account.get_debits(end=self.statementDate).order_by('-date')
        current = Decimal('0.00')
        days_31_60 = Decimal('0.00')
        days_61_90 = Decimal('0.00')
        days_90_plus = Decimal('0.00')
        balance = self.endingBalance
        for d in debits:
            days_ago = self.statementDate - d.date
            amount = min(balance, d.amount)
            if  days_ago < timedelta(days=31):
                current += amount
            elif days_ago < timedelta(days=61):
                days_31_60 += amount
            elif days_ago < timedelta(days=91):
                days_61_90 += amount
            else:
                days_90_plus += amount
            balance -= d.amount
            if balance <= Decimal('0.00'):
                break
        self.debtAge = (
                ('Current', current),
                ('31 to 60 days', days_31_60),
                ('61 to 90 days', days_61_90),
                ('Older than 90 days', days_90_plus))
    def make_html(self):
        t = Template(self.client.statementTemplate)
        c = Context({'statement': self, 'STATIC_URL': settings.STATIC_URL})
        return t.render(c)

class Scenario(models.Model):
    name = models.CharField(max_length=100, help_text='A good, descriptive name for the scenario')
    transactions = models.ManyToManyField('Transaction', blank=True)
    cctransactions = models.ManyToManyField('CCTransaction', blank=True)

class TransactionSeries(models.Model):
    name = models.CharField(max_length=100, help_text='A good, descriptive name for the series')
    startDate = models.DateField(blank=True, help_text='Date of the first transaction in the series')
    endDate = models.DateField(blank=True, help_text='Date after which the series will end.')
    repeatFormula = models.CharField(max_length=253,
            help_text='''
            The formula is specified by a series of steps.
            The steps are separated spaces.
            Each step specifies a movement.
            D = Day, M = Month, Y = Year, W = Week
            wd = workday, ME = Month End

            Y{+|-}{n}
            M{+|-|=}{n}
            W{+|-}{n}
            D{+|-|=}{n|ME}
            D{>|=>|<|<=}{wd|ME}

            Example:
            Every year on same day: Y+1
            Every month: M+1
            Every week: W+1
            3 days before month end: M+1 D=ME D-3
            first Wednesday every month: M+1 D=1 D=>Wednesday
            ''')
    scenarios = models.ManyToManyField('Scenario')
    comment = models.TextField(blank=True)

    def apply_repeat_formula(self, date):
        new_date = date
        operations = self.repeatFormula.split(' ')
        for o in operations:
            if o[0] in ('Y','y'):
                x = int(o[2:])
                if o[1] == '+':
                    new_date.year = new_date.year + x
                elif o[1] == '-': 
                    new_date.year = new_date.year - x
                else:
                    raise Exception('No valid operator specified for year')
            elif o[0] in ('M','m'):
                x = int(o[2:])
                if o[1] == '+':
                    new_month = new_date.month + x
                elif o[1] == '-': 
                    new_month = new_date.month - x
                elif o[1] == '=': 
                    new_month = x
                else:
                    raise Exception('No valid operator specified for month')
                new_month += 1
                dy = 0
                while new_month > 12:
                    dy += 1
                    new_month -= 12
                while new_month < 1:
                    dy -= 1
                    new_month += 12
                new_month_ME = datetime.date(new_date.year + dy, new_month, 1) - datetime.timedelta(1)
                new_date = datetime.date(new_month_ME.year, new_month_ME.year, min(new_date.day, new_month_ME.day))
            elif o[0] in ('W','w'):
                x = int(o[2:])
                if o[1] == '+':
                    new_date = new_date + datetime.timedelta(days=x*7)
                elif o[1] == '-': 
                    new_date = new_date - datetime.timedelta(days=x*7)
                else:
                    raise Exception('No valid operator specified for year')
            elif o[0] in ('D','d'):
                if o[1] == '+':
                    x = int(o[2:])
                    new_date = new_date + datetime.timedelta(days=x)
                elif o[1] == '-': 
                    x = int(o[2:])
                    new_date = new_date - datetime.timedelta(days=x)
                elif o[1] == '=': 
                    x = o[2:]
                    if x.lower() == 'me':
                        new_date.day = month_end(new_date)
                    else:
                        new_date.day = int(x)
                elif o[1:3] == '<=':
                    x = o[3:]
                    if x.lower() == "me":
                        if new_date != month_end(new_date):
                            new_date = datetime.date(new_date.year, new_date.month, 1) - datetime.timedelta(days=1)
                    elif x.lower() == 'wd':
                        while new_date.isoweekday in [6, 7]:
                            new_date = new_date - datetime.timedelta(1)
                elif o[1:3] == '=>':
                    x = o[3:]
                    if x.lower() == "me":
                        new_date = month_end(new_date)
                    elif x.lower() == 'wd':
                        while new_date.isoweekday in [6, 7]:
                            new_date = new_date + datetime.timedelta(1)
                elif o[1] == '>':
                    x = o[2:]
                    if x.lower() == "me":
                        new_date = month_end(new_date + datetime.timedelta(days=1))
                    elif x.lower() == 'wd':
                        new_date = new_date + datetime.timedelta(1)
                        while new_date.isoweekday in [6, 7]:
                            new_date = new_date + datetime.timedelta(1)
                elif o[1] == '<':
                    x = o[2:]
                    if x.lower() == "me":
                        new_date = datetime.date(new_date.year, new_date.month, 1) - datetime.timedelta(days=1)
                    elif x.lower() == 'wd':
                        new_date = new_date + datetime.timedelta(1)
                        while new_date.isoweekday in [6, 7]:
                            new_date = new_date + datetime.timedelta(1)
                else:
                    raise Exception('No valid operator specified for Day')
        if new_date < date:
            raise Exception('New date before old date')
        return new_date



                    



    def save(self, *args, **kwargs):
        super(TransactionSeries, self).save()
        blueprints = self.transaction_blueprints.all()
        date = self.startDate
        while date <= endDate:
            nextDate = date

class TransactionBlueprint(models.Model):
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    debitAccount = models.ForeignKey("Account", related_name="debits+")
    creditAccount = models.ForeignKey("Account", related_name="credits+")
    series = models.ForeignKey('TransactionSeries', related_name='transaction_blueprints')
    adjustment = models.CharField(max_length=253, help_text='''
        {Y|M}{+|-|*}{amount}
        Example:
            Y*1.1
            M+1000.0''')

def month_end(date):
    if date.month == 12:
        return 31
    new_date = datetime.date(date.year, date.month+1, 1) - datetime.timedelta(days=1)
    return new_date.day
