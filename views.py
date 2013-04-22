from django.shortcuts import render, get_object_or_404
from csdjango.sb import models
# Create your views here.

def account_list(request):
    accounts = models.Account.objects.all()
    return render(request, "sb/account_list.html", {"accounts": accounts})

def account_details(request, pk):
    account = get_object_or_404(models.Account, pk=pk)
    return render(request, "sb/account_detail.html", {"account": account})

def doc_list(request):
    docs = models.SourceDoc.objects.all()
    return render(request, "sb/doc_list.html", {"docs": docs})

def doc_details(request, pk):
    doc = get_object_or_404(models.SourceDoc, pk=pk)
    return render(request, "sb/doc_detail.html", {"doc": doc})

