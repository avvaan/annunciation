from modeltranslation.translator import TranslationOptions, register

from .models import Announcement, ClergyMember, PageText, SiteSettings


@register(Announcement)
class AnnouncementTranslationOptions(TranslationOptions):
    fields = ("title", "content", "link_text")


@register(ClergyMember)
class ClergyMemberTranslationOptions(TranslationOptions):
    fields = ("title", "bio")


@register(PageText)
class PageTextTranslationOptions(TranslationOptions):
    fields = ("body",)


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ("parish_name", "city", "address", "hero_lede")
