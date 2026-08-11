from django.contrib import admin, messages
from django.utils import timezone

from .models import (
    ActionItem,
    CouncilProject,
    GroupMailing,
    GroupMailingAttachment,
    Meeting,
    MeetingDocument,
    MembershipRequest,
    Protocol,
    Report,
)


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "is_council_member", "phone", "created_at"]
    list_editable = ["status", "is_council_member"]
    list_filter = ["status", "is_council_member"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "phone", "note"]
    autocomplete_fields = ["user"]
    readonly_fields = ["created_at", "approved_at", "approved_by"]
    fieldsets = (
        ("Что прислал человек", {"fields": ("user", "phone", "parish_connection", "note")}),
        ("Решение прихода", {"fields": ("status", "is_council_member", "approved_by", "approved_at")}),
        (None, {"fields": ("created_at",)}),
    )
    actions = ["approve_as_parishioner", "approve_as_council", "reject"]

    def save_model(self, request, obj, form, change):
        if obj.status == MembershipRequest.Status.APPROVED and not obj.approved_at:
            obj.approved_at = timezone.now()
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)

    def _approve(self, request, queryset, council):
        updated = 0
        for req in queryset:
            req.status = MembershipRequest.Status.APPROVED
            req.is_council_member = council
            req.approved_at = timezone.now()
            req.approved_by = request.user
            req.save()  # the post_save signal syncs the groups
            updated += 1
        self.message_user(request, f"Одобрено: {updated}.", level=messages.SUCCESS)

    @admin.action(description="Одобрить как прихожанина")
    def approve_as_parishioner(self, request, queryset):
        self._approve(request, queryset, council=False)

    @admin.action(description="Одобрить как члена совета")
    def approve_as_council(self, request, queryset):
        self._approve(request, queryset, council=True)

    @admin.action(description="Отклонить")
    def reject(self, request, queryset):
        for req in queryset:
            req.status = MembershipRequest.Status.REJECTED
            req.save()
        self.message_user(request, f"Отклонено: {queryset.count()}.", level=messages.SUCCESS)


class MeetingDocumentInline(admin.TabularInline):
    model = MeetingDocument
    extra = 0
    fields = ["title", "category", "file", "council_only", "is_published"]


class ProtocolInline(admin.TabularInline):
    model = Protocol
    extra = 0
    fields = ["title", "council_only", "is_published"]
    show_change_link = True


class ActionItemInline(admin.TabularInline):
    model = ActionItem
    extra = 0
    fk_name = "meeting"
    fields = ["title", "assignee", "due_date", "status"]
    autocomplete_fields = ["assignee"]


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "time", "status", "protocol_count", "document_count"]
    list_editable = ["status"]
    list_filter = ["status"]
    search_fields = ["title", "agenda", "location"]
    date_hierarchy = "date"
    inlines = [ProtocolInline, MeetingDocumentInline, ActionItemInline]

    @admin.display(description="Протоколов")
    def protocol_count(self, obj):
        return obj.protocols.count()

    @admin.display(description="Файлов")
    def document_count(self, obj):
        return obj.documents.count()


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ["title", "meeting", "council_only", "is_published", "created_at"]
    list_editable = ["council_only", "is_published"]
    list_filter = ["council_only", "is_published"]
    search_fields = ["title", "body", "decisions"]
    date_hierarchy = "created_at"

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "period", "council_only", "is_published", "created_at"]
    list_editable = ["council_only", "is_published"]
    list_filter = ["category", "council_only", "is_published"]
    search_fields = ["title", "body", "period"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MeetingDocument)
class MeetingDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "meeting", "category", "council_only", "is_published"]
    list_editable = ["council_only", "is_published"]
    list_filter = ["category", "council_only", "is_published"]
    search_fields = ["title", "description"]

    def save_model(self, request, obj, form, change):
        if not change and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ["title", "assignee", "due_date", "status", "meeting", "ministry", "overdue"]
    list_editable = ["status"]
    list_filter = ["status", "ministry"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["assignee"]
    actions = ["mark_done"]

    @admin.display(description="Просрочено", boolean=True)
    def overdue(self, obj):
        return obj.is_overdue

    @admin.action(description="Отметить выполненными")
    def mark_done(self, request, queryset):
        updated = queryset.update(status=ActionItem.Status.DONE)
        self.message_user(request, f"Выполнено: {updated}.", level=messages.SUCCESS)


@admin.register(CouncilProject)
class CouncilProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "owner", "due_date"]
    list_editable = ["status"]
    list_filter = ["status"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["owner"]


class GroupMailingAttachmentInline(admin.TabularInline):
    model = GroupMailingAttachment
    extra = 0


@admin.register(GroupMailing)
class GroupMailingAdmin(admin.ModelAdmin):
    list_display = ["subject", "audience_label", "recipient_count", "sent_by", "created_at"]
    list_filter = ["audience"]
    search_fields = ["subject", "body"]
    date_hierarchy = "created_at"
    inlines = [GroupMailingAttachmentInline]
    readonly_fields = ["sent_by", "recipient_count", "created_at"]

    def has_add_permission(self, request):
        # Mailings are sent from the portal, which knows the real recipient
        # list; an admin-created row would be an audit entry for an email
        # nobody ever received.
        return False
