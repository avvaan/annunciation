import datetime

from django.shortcuts import render

from .models import ServiceDay


def schedule(request):
    today = datetime.date.today()
    days = (
        ServiceDay.objects.filter(is_published=True, date__gte=today)
        .prefetch_related("items__service_type")
        .order_by("date")[:60]
    )
    return render(request, "services/schedule.html", {"days": days})
