#TabMenu
from django.conf.urls import patterns, include, url

urlpatterns = patterns('sb.views',

    url(r'^account/details/(?P<pk>\d*)/?$', 'account_details', name='account-details'),
    url(r'^accounts_summary/?$', 'trial_balance', name='trialbalance'),
    url(r'^transaction/details/(?P<pk>\d*)/?$', 'trans_details', name='transaction-details'),
    url(r'^transaction/list/?$', 'trans_list', name='transaction-list'),
    url(r'^doc/list/?$', 'doc_list', name='doc-list'),
    url(r'^doc/details/(?P<pk>\d*)/?$', 'doc_details', name='doc-details'),
    url(r'^add_payslip/(?P<employee_pk>\d*)/?$', 'add_payslip_1', name='add-payslip-1'),
    url(r'^add_payslip/?$', 'add_payslip_0', name='add-payslip'),
    url(r'^send_invoice/?$', 'send_invoice', name='send-invoice'),
    url(r'^view_invoice/(?P<invoice_nr>.*)/?$', 'view_invoice', name='view-invoice'),
    url(r'^regen_invoice/(?P<invoice_nr>.*)/?$', 'regen_invoice', name='regen-invoice'),
    url(r'^get_invoice/?$', 'get_invoice', name='get-invoice'),
    url(r'^statements/income/?$', 'income_statement', name='income-statement'),
    url(r'^extracts/(?P<dataType>.*)/?', 'extract', name='extract'),
    url(r'^apply_interest/', 'apply_interest', name='apply-interest'),
    url(r'^client_statements/?$', 'client_account_statement', name='client-statement-view'),
    url(r'^claim/new/?$', 'claim_edit', name='claim-new'),
    url(r'^claim/detail/(?P<pk>\d*)/?$', 'claim_detail', name='claim-detail'),
    url(r'^claim/submit/(?P<pk>\d*)/?$', 'submit_claim', name='claim-submit'),
    url(r'^claim/review/(?P<pk>\d*)/?$', 'review_claim', name='claim-review'),
    url(r'^claim/add/document/(?P<pk>\d*)/?$', 'claim_add_supporting_docs', name='claim-add-doc'),
    url(r'^claim/list/?$', 'claim_list', name='claim-list'),
    url(r'^charts/expenses/?$', 'expense_chart', name='chart-expense'),

)
