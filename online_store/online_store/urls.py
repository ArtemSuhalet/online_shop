from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from my_store_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_store_app.urls')),
    path('admin_app/', include('admin_app.urls', namespace='admin_app-polls')),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )