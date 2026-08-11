from modeltranslation.translator import TranslationOptions, register

from .models import RussianSchoolPage


@register(RussianSchoolPage)
class RussianSchoolPageTranslationOptions(TranslationOptions):
    fields = ("description", "schedule_text", "tuition_note")
