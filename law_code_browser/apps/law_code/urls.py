from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns(
    'law_code.views',
    (r'^(\d+)/$', 'view_code', {}, 'view-law-code'),
    (r'^(\d+)/(.*)', 'view_section', {}, 'view-code-section'),

)

