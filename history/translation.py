from modeltranslation.translator import TranslationOptions, register

from .models import HistoryMilestone


@register(HistoryMilestone)
class HistoryMilestoneTranslationOptions(TranslationOptions):
    fields = ("title", "description")
