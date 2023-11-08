from django.contrib import admin
from django.urls import path, include, re_path
import debug_toolbar
from django.views.static import serve
from ipams import settings

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('', include('records.urls')),
    path('account/', include('accounts.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]
