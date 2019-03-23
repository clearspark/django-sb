#TabMenu
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^account/details/(?P<pk>\d*)/?$', views.account_details, name='account-details'),
    url(r'^accounts_summary/?$', views.trial_balance, name='trialbalance'),
    url(r'^transaction/details/(?P<pk>\d*)/?$', views.trans_details, name='transaction-details'),
    url(r'^transaction/list/?$', views.trans_list, name='transaction-list'),
    url(r'^doc/new/?$', views.doc_new, name='document-new'),
    url(r'^doc/list/?$', views.doc_list, name='doc-list'),
    url(r'^doc/details/(?P<pk>\d*)/?$', views.doc_details, name='doc-details'),
    url(r'^series/new/?$', views.series_new, name='series-new'),
    url(r'^series/list/?$', views.series_list, name='series-list'),
    url(r'^series/details/(?P<pk>\d*)/?$', views.series_details, name='series-details'),
    url(r'^add_payslip/(?P<employee_pk>\d*)/?$', views.add_payslip_1, name='add-payslip-1'),
    url(r'^add_payslip/?$', views.add_payslip_0, name='add-payslip'),
    url(r'^send_invoice/?$', views.send_invoice, name='send-invoice'),
    url(r'^view_invoice/(?P<invoice_nr>.*)/?$', views.view_invoice, name='view-invoice'),
    url(r'^regen_invoice/(?P<invoice_nr>.*)/?$', views.regen_invoice, name='regen-invoice'),
    url(r'^get_invoice/?$', views.get_invoice, name='get-invoice'),
    url(r'^statements/income/?$', views.income_statement, name='income-statement'),
    url(r'^extracts/(?P<dataType>.*)/?', views.extract, name='extract'),
    url(r'^apply_interest/', views.apply_interest, name='apply-interest'),
    url(r'^client_statements/?$', views.client_account_statement, name='client-statement-view'),
    url(r'^claim/new/?$', views.claim_edit, name='claim-new'),
    url(r'^claim/detail/(?P<pk>\d*)/?$', views.claim_detail, name='claim-detail'),
    url(r'^claim/submit/(?P<pk>\d*)/?$', views.submit_claim, name='claim-submit'),
    url(r'^claim/review/(?P<pk>\d*)/?$', views.review_claim, name='claim-review'),
    url(r'^claim/add/document/(?P<pk>\d*)/?$', views.claim_add_supporting_docs, name='claim-add-doc'),
    url(r'^claim/list/?$', views.claim_list, name='claim-list'),
    url(r'^charts/expenses/?$', views.expense_chart, name='chart-expense'),
    url(r'^values_over_time/?$', views.values_over_time, name='values-over-time'),
    #url(r'^charts/account/timeseries/?$', 'timeseries_chart', name='chart-timeseries'),
]
