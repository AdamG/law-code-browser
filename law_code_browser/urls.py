from django.conf.urls.defaults import *
from django.conf import settings

from django.views.generic.simple import direct_to_template

from account.openid_consumer import PinaxConsumer

from django.contrib import admin
admin.autodiscover()

import os

from law_code.models import Code

def index(request):
    code_list = Code.objects.filter(public=True).order_by("name")
    return direct_to_template(
        request, 'law_code/code_list.html',
        {"code_list": code_list})


urlpatterns = patterns(
    '',
    url(r'^$', index, {}, name="home"),
    (r'^law/', include('law_code.urls')),

    (r'^about/', include('about.urls')),
    (r'^account/', include('account.urls')),
    (r'^openid/(.*)', PinaxConsumer()),
    (r'^profiles/', include('basic_profiles.urls')),
    (r'^notices/', include('notification.urls')),
    (r'^announcements/', include('announcements.urls')),

    (r'^admin/(.*)', admin.site.root),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns('', 
        (r'^site_media/(?P<path>.*)$', 'misc.views.serve')
    )
