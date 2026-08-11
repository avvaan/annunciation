from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Announcement, ClergyMember, ContactMessage, PageText, SiteSettings


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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "submitted_at", "is_read"]
    list_editable = ["is_read"]
    list_filter = ["is_read"]
    search_fields = ["name", "email", "message"]
    readonly_fields = ["name", "email", "phone", "message", "submitted_at"]
    date_hierarchy = "submitted_at"
