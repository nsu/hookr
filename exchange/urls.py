from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from exchange import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hookr.views.home', name='home'),
    # url(r'^hookr/', include('hookr.foo.urls')),
    url(r'^(?P<network>\w+)/makehookup/$', views.make_hookup),
    url(r'^(?P<network>\w+)/buyipo/$', views.order_ipo),
    url(r'^(?P<network>\w+)/buy/$', views.order),
)
