from modeltranslation.translator import TranslationOptions, register

from .models import BuildingProject, BuildingProjectUpdate


@register(BuildingProject)
class BuildingProjectTranslationOptions(TranslationOptions):
    fields = ("title", "description")


@register(BuildingProjectUpdate)
class BuildingProjectUpdateTranslationOptions(TranslationOptions):
    fields = ("title", "body")
