from django.conf.urls.defaults import *

urlpatterns = patterns('openelections.ballot.views',
    (r'^$', 'index'),
    (r'^vote$', 'vote_all'),
    (r'^choose$', 'choose_ballot'),
    (r'^record$', 'record'),
    (r'^make_json$', 'make_issues_json')

#    (r'^$', 'closed'),
#    (r'^vote$', 'closed'),
#    (r'^choose$', 'closed'),
#    (r'^record$', 'closed'),

)