import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "is_active", "subscribed_at"]
    list_filter = ["is_active"]
    search_fields = ["email", "name"]
    readonly_fields = ["confirmation_token", "unsubscribe_token", "subscribed_at", "confirmed_at"]
    fieldsets = (
        (None, {"fields": ("email", "name", "is_active")}),
        ("Служебное", {"fields": ("subscribed_at", "confirmed_at", "confirmation_token", "unsubscribe_token"),
                        "classes": ("collapse",)}),
    )
    actions = ["export_csv"]

    @admin.action(description="Экспортировать выбранных в CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(["email", "name", "is_active", "subscribed_at"])
        for s in queryset:
            writer.writerow([s.email, s.name, s.is_active, s.subscribed_at])
        return response
