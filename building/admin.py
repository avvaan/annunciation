from django.contrib import admin
from django.shortcuts import redirect
from modeltranslation.admin import TranslationAdmin

from .models import BuildingProject, BuildingProjectPhoto, BuildingProjectUpdate


class BuildingProjectUpdateInline(admin.TabularInline):
    model = BuildingProjectUpdate
    extra = 0
    fields = ["date", "title", "is_published"]
    show_change_link = True


class BuildingProjectPhotoInline(admin.TabularInline):
    model = BuildingProjectPhoto
    extra = 1


@admin.register(BuildingProject)
class BuildingProjectAdmin(TranslationAdmin):
    fieldsets = (
        (None, {"fields": ("title", "description", "cover_image", "is_active")}),
        ("Сбор средств", {"fields": ("goal_amount", "raised_amount", "raised_updated_at")}),
    )
    readonly_fields = ["raised_updated_at"]
    inlines = [BuildingProjectUpdateInline, BuildingProjectPhotoInline]

    def has_add_permission(self, request):
        return not BuildingProject.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = BuildingProject.get_solo()
        return redirect("admin:building_buildingproject_change", obj.pk)


@admin.register(BuildingProjectUpdate)
class BuildingProjectUpdateAdmin(TranslationAdmin):
    list_display = ["title", "date", "is_published"]
    list_editable = ["is_published"]
    date_hierarchy = "date"
