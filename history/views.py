from django.shortcuts import render

from .models import HistoryMilestone


def history_page(request):
    milestones = HistoryMilestone.objects.all()
    return render(request, "history/page.html", {"milestones": milestones})
