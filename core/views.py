import datetime

from django.contrib import messages
from django.shortcuts import redirect, render

from building.models import BuildingProject
from school.models import RussianSchoolPage
from services.models import ServiceDay

from .forms import ContactForm, InquiryForm
from .models import Announcement, ClergyMember, DonationPage, FirstVisitPage


def home(request):
    announcements = Announcement.objects.filter(is_active=True)
    upcoming_days = list(
        ServiceDay.objects.filter(is_published=True, date__gte=datetime.date.today())
        .prefetch_related("items__service_type")
        .order_by("date")[:4]
    )
    # Первый экран должен отвечать на вопрос, с которым сюда заходят, а не
    # повторять название прихода второй раз подряд. Ближайшая служба — это
    # первый день, где службы действительно есть.
    next_day = next((d for d in upcoming_days if d.items.all()), None)
    return render(request, "core/home.html", {
        "announcements": announcements,
        "upcoming_days": upcoming_days[:3],
        "next_day": next_day,
        "building_project": BuildingProject.get_solo(),
        "school_page": RussianSchoolPage.get_solo(),
        "first_visit": FirstVisitPage.get_solo(),
    })


def first_visit(request):
    """The newcomer's page — and the enquiry that starts a conversation."""
    if request.method == "POST":
        form = InquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Спасибо! Мы получили ваше сообщение и свяжемся с вами.",
            )
            return redirect("core:first_visit")
    else:
        form = InquiryForm()

    page = FirstVisitPage.get_solo()
    next_service = (
        ServiceDay.objects.filter(is_published=True, date__gte=datetime.date.today())
        .prefetch_related("items__service_type")
        .order_by("date")
        .first()
    )
    return render(request, "core/first_visit.html", {
        "page": page, "form": form, "next_service": next_service,
    })


def clergy(request):
    return render(request, "core/clergy.html", {
        "clergy": ClergyMember.objects.filter(is_active=True),
    })


def donation(request):
    page = DonationPage.get_solo()
    return render(request, "core/donation.html", {
        "page": page,
        "methods": page.methods.filter(is_active=True),
    })


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
