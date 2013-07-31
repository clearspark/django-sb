#TabMenu
from django.conf.urls import patterns, include, url

urlpatterns = patterns('csdjango.sb.views',

    url(r'^account/details/(?P<pk>\d*)/?$', 'account_details', name='account-details'),
    url(r'^doc/details/(?P<pk>\d*)/?$', 'doc_details', name='doc-details'),
    url(r'^transaction/details/(?P<pk>\d*)/?$', 'trans_details', name='transaction-details'),
    url(r'^transaction/list/?$', 'trans_list', name='transaction-list'),
    url(r'^doc/list/?$', 'doc_list', name='doc-list'),
    url(r'^accounts_summary/?$', 'trial_balance', name='trialbalance'),
    url(r'^add_payslip/?$', 'add_payslip', name='add-payslip'),
    url(r'^statements/income/?$', 'income_statement', name='income-statement'),
    url(r'^extracts/(?P<dataType>.*)/?', 'extract', name='extract'),

)
