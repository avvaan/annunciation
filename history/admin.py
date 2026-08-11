from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import HistoryMilestone


@admin.register(HistoryMilestone)
class HistoryMilestoneAdmin(TranslationAdmin):
    list_display = ["year", "title", "order"]
    list_editable = ["order"]
    ordering = ["order", "year"]
