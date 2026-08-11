from modeltranslation.translator import TranslationOptions, register

from .models import ServiceDay, ServiceType


@register(ServiceType)
class ServiceTypeTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(ServiceDay)
class ServiceDayTranslationOptions(TranslationOptions):
    fields = ("feast_title", "note")
