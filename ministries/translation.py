from modeltranslation.translator import TranslationOptions, register

from .models import Ministry


@register(Ministry)
class MinistryTranslationOptions(TranslationOptions):
    fields = ("name", "description", "announcement")
