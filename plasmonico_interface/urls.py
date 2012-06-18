from django.conf.urls import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^devices/$', 'devices.views.index',name='devices'),
    (r'^$', TemplateView.as_view(template_name="index.html")),
    url(r'^getcamera$', 'devices.views.getcamera', name='getcamera'),
    (r'^result.png$', 'devices.views.getImage'),
    
    #Sample rotation urls
    url(r'^sampleroation$', 'devices.views.getSampleRotationWidget',name='devices'),
    url(r'^anglescan$', 'devices.views.anglescan', name='anglescan'),
    url(r'^movesamplestage$', 'devices.views.movesamplestage', name='movesamplestage'),
    url(r'^getSampleRotationStageLocation$', 'devices.views.getSampleRotationStageLocation', name='getSampleRotationStageLocation'),
    
    #Liquid Handler- Serial Dilution Urls
    url(r'getSerialDilutionWidget$', 'devices.views.getSerialDilutionWidget', name='getSerialDilutionWidget'),
    url(r'serialDilution$', 'devices.views.serialDilution', name='serialDilution'),
    
    
    # Examples:
    # url(r'^$', 'plasmonico_interface.views.home', name='home'),
    # url(r'^plasmonico_interface/', include('plasmonico_interface.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
