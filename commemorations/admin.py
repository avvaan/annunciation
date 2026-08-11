from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Commemoration, CommemorationBatch
from .pdf import render_batch_pdf


class NoteInline(admin.TabularInline):
    model = Commemoration.batches.through
    extra = 0
    can_delete = False
    verbose_name = "записка в пачке"
    verbose_name_plural = "записки в пачке"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Commemoration)
class CommemorationAdmin(admin.ModelAdmin):
    list_display = [
        "requester_name_or_contact", "kind", "living_count", "departed_count",
        "status", "liturgies_left", "submitted_at",
    ]
    list_filter = ["kind", "status", "submitted_at"]
    search_fields = ["requester_name", "email", "phone", "living_names", "departed_names"]
    date_hierarchy = "submitted_at"
    readonly_fields = ["submitted_at", "batched_at", "printed_at", "completed_at", "batches"]
    fieldsets = (
        ("Записка", {"fields": ("kind", "living_names", "departed_names", "notes")}),
        ("Кто подал", {"fields": ("requester_name", "email", "phone")}),
        ("Печать", {"fields": (
            "status", "first_service_date", "total_liturgies", "printed_count",
            "batches", "batched_at", "printed_at", "completed_at",
        )}),
        (None, {"fields": ("submitted_at",)}),
    )
    actions = ["collect_batch"]

    @admin.display(description="Кто подал", ordering="requester_name")
    def requester_name_or_contact(self, obj):
        return obj.requester_name or obj.email or obj.phone or "—"

    @admin.display(description="О здравии")
    def living_count(self, obj):
        return len(obj.living_list) or "—"

    @admin.display(description="О упокоении")
    def departed_count(self, obj):
        return len(obj.departed_list) or "—"

    @admin.display(description="Литургий осталось")
    def liturgies_left(self, obj):
        if obj.total_liturgies <= 1:
            return "—"
        return f"{obj.remaining_liturgies} из {obj.total_liturgies}"

    @admin.action(description="Собрать в пачку и напечатать PDF")
    def collect_batch(self, request, queryset):
        """Собрать выбранные записки в один лист на жертвенник.

        Сорокоусты, у которых остались невычитанные литургии, попадают в
        пачку и остаются в работе: у них лишь растёт счётчик напечатанных.
        Разовые записки после печати закрываются.
        """
        notes = [note for note in queryset if note.is_active]
        if not notes:
            self.message_user(
                request,
                "В выборе нет записок, которые ещё нужно печатать.",
                level=messages.WARNING,
            )
            return

        today = timezone.localdate()
        batch = CommemorationBatch.objects.create(
            title=f"Записки к {today:%d.%m.%Y}", service_date=today
        )
        now = timezone.now()
        for note in notes:
            note.status = Commemoration.Status.BATCHED
            note.batched_at = now
            if note.first_service_date is None:
                note.first_service_date = today
            note.save(update_fields=["status", "batched_at", "first_service_date"])
            note.batches.add(batch)

        try:
            render_batch_pdf(batch)
        except Exception as exc:  # noqa: BLE001 — состояние пачки важнее типа сбоя
            batch.status = CommemorationBatch.Status.FAILED
            batch.error_message = str(exc)
            batch.save(update_fields=["status", "error_message"])
            self.message_user(
                request, f"Пачка собрана, но PDF не получился: {exc}",
                level=messages.ERROR,
            )
            return

        link = reverse("commemorations:batch_pdf", args=[batch.pk])
        self.message_user(
            request,
            format_html(
                'Собрано записок: {}. <a href="{}"><b>Скачать PDF</b></a>. '
                'После печати отметьте пачку напечатанной — счётчик сорокоустов сдвинется.',
                len(notes), link,
            ),
            level=messages.SUCCESS,
        )


@admin.register(CommemorationBatch)
class CommemorationBatchAdmin(admin.ModelAdmin):
    list_display = ["__str__", "service_date", "note_count", "status", "pdf_link", "created_at"]
    list_filter = ["status"]
    date_hierarchy = "created_at"
    readonly_fields = ["status", "pdf_link", "error_message", "created_at", "printed_at"]
    fields = ["title", "service_date", "status", "pdf_link", "error_message",
              "created_at", "printed_at"]
    inlines = [NoteInline]
    actions = ["rebuild_pdf", "mark_printed"]

    def has_add_permission(self, request):
        # Пачку собирают действием на списке записок — оно знает, какие
        # записки в неё входят. Пустая пачка из админки была бы записью
        # о листе, которого никто не печатал.
        return False

    @admin.display(description="Записок")
    def note_count(self, obj):
        return obj.note_count

    @admin.display(description="PDF")
    def pdf_link(self, obj):
        if not obj.pdf_file:
            return "—"
        return format_html(
            '<a href="{}">Скачать</a>',
            reverse("commemorations:batch_pdf", args=[obj.pk]),
        )

    @admin.action(description="Пересобрать PDF")
    def rebuild_pdf(self, request, queryset):
        rebuilt = 0
        for batch in queryset:
            try:
                render_batch_pdf(batch)
                rebuilt += 1
            except Exception as exc:  # noqa: BLE001
                self.message_user(
                    request, f"{batch}: {exc}", level=messages.ERROR
                )
        if rebuilt:
            self.message_user(request, f"Пересобрано: {rebuilt}.", level=messages.SUCCESS)

    @admin.action(description="Отметить напечатанной")
    def mark_printed(self, request, queryset):
        for batch in queryset:
            for note in batch.notes.all():
                note.mark_printed()
            batch.status = CommemorationBatch.Status.PRINTED
            batch.printed_at = timezone.now()
            batch.save(update_fields=["status", "printed_at"])
        self.message_user(
            request,
            f"Отмечено напечатанными: {queryset.count()}. "
            "Сорокоусты с остатком снова в очереди.",
            level=messages.SUCCESS,
        )
