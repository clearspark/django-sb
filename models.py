from django.db import models
#from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=200)
    cat = models.CharField(max_length=200, choices=(("equity", "Equity"), ("negEq", "Negative equity"), ("asset", "Asset"), ("liability", "Liability"), ("income", "Income"), ("expense", "Expence")))
    parent = models.ForeignKey("self", related_name="children", null=True, blank=True)
    def __unicode__(self):
        return self.name
    def transactions(self):
        return Transactions.objects.filter( models.Q(debitAccount=self) | models.Q(creditAccount=self)).all()
    def balance(self):
        debitTotal = sum(self.debits.all().values_list("amount", flat=True))
        creditTotal = sum(self.credits.all().values_list("amount", flat=True))
        return debitTotal - creditTotal
    def pretty_balance(self):
        balance = self.balance()
        if balance >= 0:
            return "Dr {}".format(balance)
        else:
            return "Cr {}".format(balance)

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
    
class Transaction(models.Model):
    debitAccount = models.ForeignKey("Account", related_name="debits")
    creditAccount = models.ForeignKey("Account", related_name="credits")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    date = models.DateField()
    recordedTime = models.DateTimeField(auto_now=True)
    recordedBy = models.ForeignKey("auth.User", editable=False)
    sourceDocument = models.ForeignKey(SourceDoc, blank=True, null=True)
    comments = models.TextField(blank=True)
    isConfirmed = models.BooleanField()
    def __unicode__(self):
        return "{} {}:{} {}".format(self.date, self.debitAccount, self.creditAccount, self.amount)
