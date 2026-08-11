from modeltranslation.translator import TranslationOptions, register

from .models import (
    Announcement,
    ClergyMember,
    DonationMethod,
    DonationPage,
    FirstVisitPage,
    PageText,
    SiteSettings,
)


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


@register(FirstVisitPage)
class FirstVisitPageTranslationOptions(TranslationOptions):
    fields = ("intro", "when_text", "what_to_expect", "practical", "communion_note")


@register(DonationPage)
class DonationPageTranslationOptions(TranslationOptions):
    fields = ("intro",)


@register(DonationMethod)
class DonationMethodTranslationOptions(TranslationOptions):
    fields = ("title", "description", "button_label")
