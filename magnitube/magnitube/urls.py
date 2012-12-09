from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'downloader.views.index', name='home'),
    url(r'^process/$', 'downloader.views.process_download_request', name='process'),
    url(r'^([-\w]+)/$', 'downloader.views.show_list', name='show_list'),
    url(r'^([-\w]+)/(\d+)/view/$', 'downloader.views.view', name='view'),
    url(r'^([-\w]+)/(\d+)/.*$', 'downloader.views.download', name='download'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
