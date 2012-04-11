from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()
admin.site.login_template = 'webauth/admin_redirect.html'

urlpatterns = patterns('',
    (r'^$', 'openelections.ballot.views.landing'),
#    (r'^ballot-test1234/', include('openelections.ballot.urls')),
#    (r'^$', 'openelections.ballot.views.redirect'),
    (r'^ballot/', include('openelections.ballot.urls')),
    (r'^ballot_admin/', include('openelections.ballot_admin.urls')),

#    (r'^$','openelections.issues.views.index'),
#    (r'^petitions/', include('openelections.petitions.urls')),
    (r'^issues/', include('openelections.issues.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^webauth/', include('openelections.webauth.urls')),

   (r'^media/(?P<path>.*)$', 'django.views.static.serve',
           {'document_root': 'public/media/'}),

#   (r'^(?P<issue_slug>[\w\d-]+)$', 'openelections.issues.views.detail'),

   (r'^accounts/login/$', 'webauth.views.login')
)
