import datetime

from django.contrib import admin, messages
from modeltranslation.admin import TranslationAdmin

from .models import (
    WEEKDAY_NAMES_RU,
    RecurringServiceItem,
    RecurringServiceRule,
    ServiceDay,
    ServiceItem,
    ServiceType,
)


@admin.register(ServiceType)
class ServiceTypeAdmin(TranslationAdmin):
    list_display = ["name", "order"]
    list_editable = ["order"]


class RecurringServiceItemInline(admin.TabularInline):
    model = RecurringServiceItem
    extra = 1


@admin.register(RecurringServiceRule)
class RecurringServiceRuleAdmin(admin.ModelAdmin):
    list_display = ["title", "weekday", "default_fasting_level", "is_active"]
    list_editable = ["is_active"]
    inlines = [RecurringServiceItemInline]
    actions = ["generate_next_4_weeks", "generate_next_8_weeks"]

    @admin.action(description="Сгенерировать службы на 4 недели вперёд")
    def generate_next_4_weeks(self, request, queryset):
        self._generate(request, queryset, weeks=4)

    @admin.action(description="Сгенерировать службы на 8 недель вперёд")
    def generate_next_8_weeks(self, request, queryset):
        self._generate(request, queryset, weeks=8)

    def _generate(self, request, queryset, weeks):
        today = datetime.date.today()
        created_days = 0
        created_items = 0
        for rule in queryset.filter(is_active=True):
            items = list(rule.items.all())
            if not items:
                continue
            date = today
            # advance to the first occurrence of the rule's weekday
            while date.weekday() != rule.weekday:
                date += datetime.timedelta(days=1)
            end = today + datetime.timedelta(weeks=weeks)
            while date <= end:
                day, day_created = ServiceDay.objects.get_or_create(
                    date=date,
                    defaults={
                        "fasting_level": rule.default_fasting_level,
                        "generated_from_rule": rule,
                    },
                )
                if day_created:
                    created_days += 1
                for item in items:
                    _, item_created = ServiceItem.objects.get_or_create(
                        day=day, service_type=item.service_type, time=item.time,
                        defaults={"note": item.note, "order": item.order},
                    )
                    if item_created:
                        created_items += 1
                date += datetime.timedelta(weeks=1)
        self.message_user(
            request,
            f"Создано дней: {created_days}, служб добавлено: {created_items}. "
            "Уже существующие дни не тронуты — правьте их вручную под праздники и посты.",
            level=messages.SUCCESS,
        )


class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 1


@admin.register(ServiceDay)
class ServiceDayAdmin(TranslationAdmin):
    list_display = ["date", "weekday_label", "old_style_label", "feast_title",
                    "is_major", "fasting_level", "is_published"]
    list_editable = ["is_major", "is_published"]
    list_filter = ["fasting_level", "is_major", "is_published"]
    search_fields = ["feast_title", "note"]
    date_hierarchy = "date"
    inlines = [ServiceItemInline]
    actions = ["duplicate_to_next_week"]

    @admin.display(description="День недели")
    def weekday_label(self, obj):
        return WEEKDAY_NAMES_RU[obj.date.weekday()]

    @admin.display(description="Ст. стиль")
    def old_style_label(self, obj):
        return obj.old_style_date.strftime("%d.%m")

    @admin.action(description="Скопировать на следующую неделю (+7 дней)")
    def duplicate_to_next_week(self, request, queryset):
        created = 0
        for day in queryset:
            new_date = day.date + datetime.timedelta(weeks=1)
            new_day, was_created = ServiceDay.objects.get_or_create(
                date=new_date,
                defaults={
                    "feast_title": "",
                    "fasting_level": day.fasting_level,
                    "note": "",
                    "is_published": day.is_published,
                },
            )
            if was_created:
                created += 1
                for item in day.items.all():
                    ServiceItem.objects.create(
                        day=new_day, service_type=item.service_type,
                        time=item.time, note=item.note, order=item.order,
                    )
        self.message_user(request, f"Создано новых дней: {created}.", level=messages.SUCCESS)
