from datetime import datetime, timedelta

from django.db import models
from django.core.urlresolvers import reverse
from django.template import Template, Context
#from mptt.models import MPTTModel, TreeForeignKey

ACCOUNT_CATEGORIES = (("equity", "Equity"), ("asset", "Asset"), ("liability", "Liability"), ("income", "Income"), ("expense", "Expense"))
INCOME_STATEMENT_CATS = ('income', 'expense',)
BALANCE_SHEET_CATS = ('equity', 'asset', 'liability',)
# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    cat = models.CharField(max_length=200, choices=ACCOUNT_CATEGORIES)
    gl_code = models.CharField(max_length=20, blank=True)
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True)
    class Meta:
        ordering = ["name"]
    def long_name(self):
        if self.parent:
            return self.parent.__unicode__()+" > "+self.name
        else:
            return self.name
    def long_href(self):
        if self.parent:
            return self.parent.href()+"&gt"+self.href()
        else:
            return self.href()
    def __unicode__(self):
        return self.long_name()
    def transactions(self):
        return Transaction.objects.filter( models.Q(debitAccount=self) | models.Q(creditAccount=self)).order_by("date").all()
    def get_transactions(self, begin=None, end=None):
        transactions = self.transactions()
        if begin is not None:
            transactions = transactions.filter(date__gte=begin)
        if end is not None:
            transactions = transactions.filter(date__lte=end)
        return transactions
    def get_debits(self, begin=None, end=None):
        debits = self.debits
        if begin is not None:
            debits = debits.filter(date__gte = begin)
        if end is not None:
            debits = debits.filter(date__lte = end)
        return debits
    def get_credits(self, begin=None, end=None):
        credits = self.credits
        if begin is not None:
            credits = credits.filter(date__gte = begin)
        if end is not None:
            credits = credits.filter(date__lte = end)
        return credits
    def dt_sum(self, *args, **kwargs):
        return sum(self.get_debits(*args, **kwargs).all().values_list("amount", flat=True))
    def ct_sum(self,  *args, **kwargs):
        return sum(self.get_credits(*args, **kwargs).all().values_list("amount", flat=True))
    def balance(self, *args, **kwargs):
        return self.dt_sum(*args, **kwargs) - self.ct_sum(*args, **kwargs)
    def ct_balance(self):
        return -self.balance()
    def pretty_balance(self, *args, **kwargs):
        balance = self.balance(*args, **kwargs)
        if balance >= 0:
            return "Dr {}".format(balance)
        else:
            return "Cr {}".format(-balance)
    def get_average_balance(self, begin, end):
        num_days = (end - begin).days + 1
        print 'num_days', num_days
        avg_balance = self.balance(end=(begin-timedelta(days=1)))
        print 'starting balance', avg_balance
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
    invoiceTemplate = models.TextField(blank=True)
    statementTemplate = models.TextField(blank=True)
    invoice_suffix = models.CharField(max_length=12)
    def __unicode__(self):
        return self.displayName

def source_doc_file_path(instance, filename):
    return "sb/src_docs/{}/{}".format(instance.number, filename)
class SourceDoc(models.Model):
    number = models.CharField(max_length=40, unique=True, help_text="Document number")
    electronicCopy = models.FileField(upload_to=source_doc_file_path, blank=True, null=True, verbose_name="Electronic copy")
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    comments = models.TextField(blank=True)
    docType = models.CharField(max_length=20, choices=(
        ('bank-statement', 'Bank statement'),
        ('invoice-out', 'Outbound invoice'),
        ('invoice-in', 'Inbound invoice'),
        ('payslip', 'Payslip'),
        ('other', 'Other')),
        help_text='The type of document being recorded/created')
    def __unicode__(self):
        return unicode(self.number)
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

def get_new_invoice_nr(client):
    num = Invoice.objects.filter(client=client).count() + 1
    return "CS%04d-%s" %(num, client.invoice_suffix)

class Invoice(SourceDoc):
    client = models.ForeignKey('Client')
    html = models.TextField(blank=True)
    finalized = models.BooleanField(default=False)
    def __unicode__(self):
        return self.number
    def get_total_excl(self):
        return self.invoiceline_set.aggregate(models.Sum('amount'))['amount__sum']
    def get_total_vat(self):
        return self.invoiceline_set.aggregate(models.Sum('vat'))['vat__sum']
    def get_total_incl(self):
        return self.get_total_excl() + self.get_total_vat()
    def make_html(self):
        t = Template(self.client.invoiceTemplate)
        c = Context({'invoice': self})
        return t.render(c)

class InvoiceLine(models.Model):
    invoice = models.ForeignKey('Invoice')
    description = models.CharField(max_length=1000)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    vat = models.DecimalField(max_digits=16, decimal_places=2)

class Transaction(models.Model):
    debitAccount = models.ForeignKey("Account", related_name="debits")
    creditAccount = models.ForeignKey("Account", related_name="credits")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    date = models.DateField()
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    sourceDocument = models.ForeignKey(SourceDoc, related_name="transactions", blank=True, null=True)
    comments = models.TextField(blank=True)
    isConfirmed = models.BooleanField()
    class Meta:
        ordering = ["date", "recordedTime"]
    def __unicode__(self):
        return "{} {}:{} {}".format(self.date, self.debitAccount, self.creditAccount, self.amount)
    def date_href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.date)
    def get_absolute_url(self):
        return reverse("transaction-details", kwargs={"pk": self.pk})

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
    def __unicode__(self):
        return self.user.get_full_name()
