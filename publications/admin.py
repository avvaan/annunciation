from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Publication


@admin.register(Publication)
class PublicationAdmin(TranslationAdmin):
    list_display = ["title", "kind", "period_label", "published_at", "is_published"]
    list_editable = ["is_published"]
    list_filter = ["kind", "is_published"]
    date_hierarchy = "published_at"
