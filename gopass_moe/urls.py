from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gopass_moe.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    #url(r'^proxy_auth/', include('acgproxy.urls', namespace='acgproxy', app_name='acgproxy')),
    url(r'^', include('kotoridb.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

