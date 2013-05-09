from django.db import models
from django.core.urlresolvers import reverse
#from mptt.models import MPTTModel, TreeForeignKey

ACCOUNT_CATEGORIES = (("equity", "Equity"), ("asset", "Asset"), ("liability", "Liability"), ("income", "Income"), ("expense", "Expense"))
# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    cat = models.CharField(max_length=200, choices=ACCOUNT_CATEGORIES)
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
    def pretty_balance(self, *args, **kwargs):
        balance = self.balance(*args, **kwargs)
        if balance >= 0:
            return "Dr {}".format(balance)
        else:
            return "Cr {}".format(-balance)
    def dt_count(self, *args, **kwargs):
        return self.get_debits(*args, **kwargs).all().count()
    def ct_count(self, begin=None, end=None):
        return self.get_credits(*args, **kwargs).all().count()
    def t_count(self, *args, **kwargs):
        return self.get_transactions(*args, **kwargs).count()
    def get_absolute_url(self):
        return reverse("account-details", kwargs={"pk": self.pk})
    def href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.name)

def source_doc_file_path(instance, filename):
    return "sb/{}/{}".format(instance.number, filename)
class SourceDoc(models.Model):
    number = models.CharField(max_length=40, unique=True)
    electronicCopy = models.FileField(upload_to=source_doc_file_path, blank=True, null=True)
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    comments = models.TextField(blank=True)
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

