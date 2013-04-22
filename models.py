from django.db import models
from django.core.urlresolvers import reverse
#from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    cat = models.CharField(max_length=200, choices=(("equity", "Equity"), ("negEq", "Negative equity"), ("asset", "Asset"), ("liability", "Liability"), ("income", "Income"), ("expense", "Expense")))
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True)
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
        return Transaction.objects.filter( models.Q(debitAccount=self) | models.Q(creditAccount=self)).all()
    def dt_sum(self):
        return sum(self.debits.all().values_list("amount", flat=True))
    def ct_sum(self):
        return sum(self.credits.all().values_list("amount", flat=True))
    def balance(self):
        return self.dt_sum() - self.ct_sum()
    def pretty_balance(self):
        balance = self.balance()
        if balance >= 0:
            return "Dr {}".format(balance)
        else:
            return "Cr {}".format(-balance)
    def dt_count(self):
        return self.debits.all().count()
    def ct_count(self):
        return self.credits.all().count()
    def t_count(self):
        return self.dt_counts() + self.ct_counts()
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
        return self.transaction_set.all().count()
    def get_absolute_url(self):
        return reverse("doc-details", kwargs={"pk": self.pk})
    def href(self):
        return '<a href="%s">%s</a>' %(self.get_absolute_url(), self.number)
    
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
        ordering = ["date"]
    def __unicode__(self):
        return "{} {}:{} {}".format(self.date, self.debitAccount, self.creditAccount, self.amount)
