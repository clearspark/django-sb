#TabMenu
from django.conf.urls import patterns, include, url

urlpatterns = patterns('csdjango.sb.views',

    url(r'^account/details/(?P<pk>\d*)$', 'account_details', name='account-details'),
    url(r'^doc/details/(?P<pk>\d*)$', 'doc_details', name='doc-details'),

)
