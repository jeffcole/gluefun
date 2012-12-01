"""
Django URL configuration for the gluefun app.
"""


from django.conf.urls import patterns, include, url


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gluefun.views.home', name='home'),
    # url(r'^gluefun/', include('gluefun.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('gluefun.views',
    url(r'^$', 'login'),
    url(r'^home/$', 'home'),
    url(r'^results/$', 'results'),
)
