from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include, path
from my_store_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_store_app.urls')),
]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )