from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore

from django.conf.urls.static import static #static is a function that we need # type: ignore
from django.conf import settings # type: ignore

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inicial.urls")),
    path("autoescola/", include("autoescola.urls")),
    path("politicas/", include("politicas.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)