from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("schedule/", include("services.urls")),
    path("publications/", include("publications.urls")),
    path("building-project/", include("building.urls")),
    path("russian-school/", include("school.urls")),
    path("history/", include("history.urls")),
    path("newsletter/", include("newsletter.urls")),
    path("ministries/", include("ministries.urls")),
    path("council/", include("council.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
