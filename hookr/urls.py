from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login, logout
admin.autodiscover()
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hookr.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^', include('exchange.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login',
    {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)
