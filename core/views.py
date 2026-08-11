import datetime

from django.contrib import messages
from django.shortcuts import redirect, render

from services.models import ServiceDay

from .forms import ContactForm
from .models import Announcement, ClergyMember


def home(request):
    announcements = Announcement.objects.filter(is_active=True)
    upcoming_days = (
        ServiceDay.objects.filter(is_published=True, date__gte=datetime.date.today())
        .prefetch_related("items__service_type")
        .order_by("date")[:3]
    )
    return render(request, "core/home.html", {"announcements": announcements, "upcoming_days": upcoming_days})


def about(request):
    clergy = ClergyMember.objects.filter(is_active=True)
    return render(request, "core/about.html", {"clergy": clergy})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Сообщение отправлено. Мы ответим вам в ближайшее время.")
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})
