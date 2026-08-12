import datetime
import itertools

from django.shortcuts import render
from django.utils import timezone

from .models import MONTH_NOMINATIVE, ServiceDay


def schedule(request):
    """Расписание богослужений.

    Раньше вьюха отдавала шестьдесят дней одним плоским списком, и человек
    сам искал в нём сегодняшнее число. Здесь два разных вопроса разделены:
    «когда ближайшая служба» — отдельным блоком наверху, «что дальше» —
    списком, разбитым по месяцам.
    """
    today = timezone.localdate()
    days = list(
        ServiceDay.objects.filter(is_published=True, date__gte=today)
        .prefetch_related("items__service_type")
        .order_by("date")[:60]
    )

    # Ближайшая — первая, где действительно есть службы: день, отмеченный
    # только степенью поста, на вопрос «когда идти» не отвечает.
    next_day = next((d for d in days if d.items.all()), None)

    months = [
        {
            "label": MONTH_NOMINATIVE[key[1] - 1],
            "year": key[0],
            "show_year": key[0] != today.year,
            "days": list(group),
        }
        for key, group in itertools.groupby(days, key=lambda d: (d.date.year, d.date.month))
    ]

    return render(request, "services/schedule.html", {
        "days": days,
        "next_day": next_day,
        "months": months,
        "today": today,
    })
