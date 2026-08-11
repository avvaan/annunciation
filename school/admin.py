from django.contrib import admin
from django.shortcuts import redirect
from modeltranslation.admin import TranslationAdmin

from .models import RussianSchoolPage, RussianSchoolPhoto


class RussianSchoolPhotoInline(admin.TabularInline):
    model = RussianSchoolPhoto
    extra = 1


@admin.register(RussianSchoolPage)
class RussianSchoolPageAdmin(TranslationAdmin):
    fieldsets = (
        (None, {"fields": ("description", "cover_image", "age_from", "schedule_text")}),
        ("Учебный год", {"fields": ("term_start", "term_end", "tuition_note", "enrollment_open")}),
        ("Контакты", {"fields": ("contact_email", "contact_phone")}),
    )
    inlines = [RussianSchoolPhotoInline]

    def has_add_permission(self, request):
        return not RussianSchoolPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = RussianSchoolPage.get_solo()
        return redirect("admin:school_russianschoolpage_change", obj.pk)
