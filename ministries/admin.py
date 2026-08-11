from django.contrib import admin, messages
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from .models import (
    Ministry,
    MinistryAttachment,
    MinistryComment,
    MinistryDocument,
    MinistryMembership,
    MinistryPhoto,
    MinistryProject,
    MinistryReport,
    MinistryScheduleEntry,
    MinistrySupplyRequest,
    MinistryTopic,
)


class MinistryMembershipInline(admin.TabularInline):
    model = MinistryMembership
    extra = 0
    autocomplete_fields = ["user"]
    fields = ["user", "role", "status"]


class MinistryProjectInline(admin.TabularInline):
    model = MinistryProject
    extra = 0
    fields = ["title", "status", "due_date", "owner"]
    show_change_link = True


@admin.register(Ministry)
class MinistryAdmin(TranslationAdmin):
    list_display = ["thumb", "name", "is_active", "is_private", "order", "member_count", "project_count"]
    list_editable = ["is_active", "is_private", "order"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["leaders"]
    inlines = [MinistryMembershipInline, MinistryProjectInline]

    @admin.display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:32px;border-radius:4px">', obj.image.url)
        return "—"

    @admin.display(description="Участников")
    def member_count(self, obj):
        return obj.memberships.filter(status=MinistryMembership.Status.ACTIVE).count()

    @admin.display(description="Проектов")
    def project_count(self, obj):
        return obj.projects.count()


@admin.register(MinistryMembership)
class MinistryMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "ministry", "role", "status", "created_at"]
    list_filter = ["ministry", "role", "status"]
    list_editable = ["role", "status"]
    autocomplete_fields = ["user"]
    actions = ["approve_memberships"]

    @admin.action(description="Одобрить заявки")
    def approve_memberships(self, request, queryset):
        updated = queryset.filter(status=MinistryMembership.Status.PENDING).update(
            status=MinistryMembership.Status.ACTIVE, approved_by=request.user
        )
        self.message_user(request, f"Одобрено: {updated}.", level=messages.SUCCESS)


@admin.register(MinistryProject)
class MinistryProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "ministry", "status", "due_date", "owner"]
    list_filter = ["ministry", "status"]
    list_editable = ["status"]


@admin.register(MinistryTopic)
class MinistryTopicAdmin(admin.ModelAdmin):
    list_display = ["title", "ministry", "author", "is_pinned", "created_at"]
    list_filter = ["ministry", "is_pinned"]
    list_editable = ["is_pinned"]


@admin.register(MinistryComment)
class MinistryCommentAdmin(admin.ModelAdmin):
    list_display = ["topic", "author", "created_at"]
    list_filter = ["topic__ministry"]


@admin.register(MinistryAttachment)
class MinistryAttachmentAdmin(admin.ModelAdmin):
    list_display = ["file", "topic", "comment", "uploaded_at"]


@admin.register(MinistryDocument)
class MinistryDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "ministry", "category", "visibility", "uploaded_at"]
    list_filter = ["ministry", "category", "visibility"]

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MinistryReport)
class MinistryReportAdmin(admin.ModelAdmin):
    list_display = ["title", "ministry", "period", "visibility", "created_at"]
    list_filter = ["ministry", "visibility"]

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MinistryPhoto)
class MinistryPhotoAdmin(admin.ModelAdmin):
    list_display = ["thumb", "ministry", "caption", "uploaded_at"]
    list_filter = ["ministry"]

    @admin.display(description="")
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:32px;border-radius:4px">', obj.image.url)
        return "—"

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MinistryScheduleEntry)
class MinistryScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ["ministry", "date", "person", "second_person"]
    list_filter = ["ministry"]
    date_hierarchy = "date"


@admin.register(MinistrySupplyRequest)
class MinistrySupplyRequestAdmin(admin.ModelAdmin):
    list_display = ["item", "ministry", "status", "requested_by", "created_at"]
    list_filter = ["ministry", "status"]
    list_editable = ["status"]
