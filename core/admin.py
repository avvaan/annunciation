from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    Announcement,
    ClergyMember,
    ContactMessage,
    DonationMethod,
    DonationPage,
    FirstVisitPage,
    Inquiry,
    PageText,
    SiteSettings,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin):
    fieldsets = (
        ("Приход", {"fields": ("parish_name", "city", "address", "phone", "email")}),
        ("Первый экран", {
            "fields": ("hero_image", "hero_lede"),
            "description": "Горизонтальное фото храма, шириной не меньше 2000 px — "
                           "оно обрезается по размеру экрана.",
        }),
        ("Realm (членство и пожертвования)", {
            "fields": ("realm_giving_url", "realm_membership_url", "realm_embed_code"),
        }),
        ("Соцсети", {"fields": ("facebook_url", "instagram_url", "youtube_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.get_solo()
        from django.shortcuts import redirect
        return redirect("admin:core_sitesettings_change", obj.pk)


@admin.register(PageText)
class PageTextAdmin(TranslationAdmin):
    list_display = ["label", "page", "block", "updated_at"]
    list_filter = ["page"]
    readonly_fields = ["page", "block", "label"]
    fields = ["page", "block", "label", "body"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Announcement)
class AnnouncementAdmin(TranslationAdmin):
    list_display = ["title", "is_active", "order", "created_at"]
    list_editable = ["is_active", "order"]
    list_filter = ["is_active"]
    search_fields = ["title", "content"]


@admin.register(ClergyMember)
class ClergyMemberAdmin(TranslationAdmin):
    list_display = ["name", "title", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(FirstVisitPage)
class FirstVisitPageAdmin(TranslationAdmin):
    fieldsets = (
        (None, {"fields": ("intro",)}),
        ("Служба", {"fields": ("when_text", "what_to_expect")}),
        ("Практическое", {"fields": ("practical", "communion_note")}),
    )

    def has_add_permission(self, request):
        return not FirstVisitPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:core_firstvisitpage_change", FirstVisitPage.get_solo().pk)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "about", "preferred_contact", "submitted_at", "is_handled"]
    list_editable = ["is_handled"]
    list_filter = ["about", "is_handled"]
    search_fields = ["name", "email", "phone", "message"]
    date_hierarchy = "submitted_at"
    readonly_fields = [
        "name", "email", "phone", "about", "preferred_contact",
        "best_time", "message", "submitted_at",
    ]
    fieldsets = (
        ("Что прислал человек", {
            "fields": ("name", "email", "phone", "about", "preferred_contact", "best_time", "message"),
        }),
        ("Приход", {"fields": ("is_handled", "submitted_at")}),
    )

    def has_add_permission(self, request):
        return False


class DonationMethodInline(admin.TabularInline):
    model = DonationMethod
    extra = 1


@admin.register(DonationPage)
class DonationPageAdmin(TranslationAdmin):
    inlines = [DonationMethodInline]

    def has_add_permission(self, request):
        return not DonationPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:core_donationpage_change", DonationPage.get_solo().pk)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "submitted_at", "is_read"]
    list_editable = ["is_read"]
    list_filter = ["is_read"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "phone", "message", "submitted_at"]
    date_hierarchy = "submitted_at"
